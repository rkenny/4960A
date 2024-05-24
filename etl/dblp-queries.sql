
      select distinct keywordId, authorId
        from paper_keyword_author
into outfile '/var/lib/mysql-files/dblp/user_item.txt';

     select distinct paperId, authorId
       from paper_keyword_author   
into outfile '/var/lib/mysql-files/dblp/bundle_item.txt';

      select distinct keywordId, authorId
        from paper_keyword_author
       where paperId not in (select paperId from paper_keyword_author where paperId like '%__%3%3%')
into outfile '/var/lib/mysql-files/dblp/user_bundle_train.txt';

      select distinct keywordId, authorId
        from paper_keyword_author
       where paperId in (select paperId from paper_keyword_author where paperId like '%__%3%3%')
into outfile '/var/lib/mysql-files/dblp/user_bundle_test.txt';

      select distinct keywordId, authorId
        from paper_keyword_author
       where paperId in (select paperId from paper_keyword_author where paperId like '%__3%4%')
into outfile '/var/lib/mysql-files/dblp/user_bundle_tune.txt';

      select sum(case when col = 'UserCount' then val else 0 end) as UserCount,
             sum(case when col = 'BundleCount' then val else 0 end) as BundleCount,
             sum(case when col = 'ItemCount' then val else 0 end) as ItemCount
        from (      select count(distinct paperId) as val, 'BundleCount' as col from paper_keyword_author
              union select count(distinct keywordId) as val, 'UserCount' as col from paper_keyword_author
              union select count(distinct authorId) as val, 'ItemCount' as col from paper_keyword_author
             ) samples
into outfile '/var/lib/mysql-files/dblp/dblp_data_size.txt';
