drop table if exists sample_paper;
create temporary table if not exists sample_paper as (
  select distinct paperId
    from paper_author
group by paperId
   having count(authorId) >= 2
);

drop table if exists smaller_sample_paper;
create temporary table if not exists smaller_sample_paper as (
    select distinct keyword_paper.paperId
      from keyword_paper
inner join sample_paper
        on sample_paper.paperId = keyword_paper.paperId
  group by keyword_paper.paperId
    having count(keyword_paper.keywordId) >= 5  
); 

drop table if exists sample_keyword;
create temporary table if not exists sample_keyword as (
    select distinct keywordId
      from keyword_paper
inner join smaller_sample_paper
        on smaller_sample_paper.paperId = keyword_paper.paperId
); 
        
    select distinct keyword_author.keywordId, keyword_author.authorId
      from keyword_author
inner join sample_keyword
        on sample_keyword.keywordId = keyword_author.keywordId
  order by keyword_author.authorId
into outfile '/var/lib/mysql-files/user_item.txt';

-- get bundle_item for teams >= 15
    select paper_author.paperId, authorId
      from paper_author
inner join smaller_sample_paper
        on smaller_sample_paper.paperId = paper_author.paperId
  order by paper_author.paperId
 into outfile '/var/lib/mysql-files/bundle_item.txt';


   
-- user_bundle (train) = keyword_paper
    select distinct keyword_paper.keywordId, keyword_paper.paperId
      from keyword_paper
inner join smaller_sample_paper
        on smaller_sample_paper.paperId = keyword_paper.paperId
     where smaller_sample_paper.paperId not like '%832%' -- random set of 7552 papers chosen for testing
           and smaller_sample_paper.paperId not like '%811%' -- random set of 7952 papers chosen for tuning
  order by keyword_paper.paperId, keyword_paper.keywordId
into outfile '/var/lib/mysql-files/user_bundle_train.txt';
    
-- user_bundle (test) = keyword_paper
    select distinct keyword_paper.keywordId, keyword_paper.paperId
      from keyword_paper
inner join smaller_sample_paper
        on smaller_sample_paper.paperId = keyword_paper.paperId
     where smaller_sample_paper.paperId like '%832%' -- random set of 7552 papers chosen for testing
  order by keyword_paper.paperId, keyword_paper.keywordId
into outfile '/var/lib/mysql-files/user_bundle_test.txt';


-- user_bundle (tune) = keyword_paper
    select distinct keyword_paper.keywordId, keyword_paper.paperId
      from keyword_paper
inner join smaller_sample_paper
        on smaller_sample_paper.paperId = keyword_paper.paperId
     where smaller_sample_paper.paperId like '%811%' -- random set of 7952 papers chosen for tuning
  order by keyword_paper.paperId, keyword_paper.keywordId
into outfile '/var/lib/mysql-files/user_bundle_tune.txt';

drop table if exists sampled_authors;

create temporary table if not exists sampled_authors as
select count(distinct authorId) as val, 'ItemCount' as col
  from paper_author
 where paperId in (select paperId from smaller_sample_paper);
              

select sum(case when col = 'UserCount' then val else 0 end) as UserCount,
       sum(case when col = 'BundleCount' then val else 0 end) as BundleCount,
       sum(case when col = 'ItemCount' then val else 0 end) as ItemCount
  from (select count(distinct keywordId) as val, 'UserCount' as col from sample_keyword
        union select count(distinct paperId) as val, 'BundleCount' as col from smaller_sample_paper
        union (select val, col from sampled_authors) 
       ) samples
into outfile '/var/lib/mysql-files/dblp_data_size.txt';
