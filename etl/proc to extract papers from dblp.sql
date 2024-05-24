drop procedure if exists paper_proc;
delimiter //
create procedure paper_proc()
  begin
    declare done int default 0;
    declare paperIdVar varchar(12);
    declare authorIdVar varchar(12);
    declare paper_cursor cursor for 
      select paperId, authorId from paper_author limit 1;
    declare continue handler for not found set done = 1;
    open paper_cursor;
papers: loop
    fetch paper_cursor into paperIdVar, authorIdVar;
    if done = 1 then
      leave papers;
    end if;
    -- keyword - paper
        select distinct keyword_paper.keywordId, keyword_paper.paperId
          from keyword_paper
         where keyword_paper.paperId = paperIdVar;
         
    -- keyword - author
        select distinct keyword_paper.keywordId, authorId
          from keyword_paper
    inner join paper_author
            on keyword_paper.paperid = paper_author.paperid
         where paper_author.paperid = paperIdVar;

        select distinct keyword_paper.keywordId, keyword_paper.paperId
          from keyword_paper
    inner join paper_author
            on keyword_paper.paperid = paper_author.paperid
         where paper_author.paperid = paperIdVar;
         
end loop papers;
    close paper_cursor;
  end//
delimiter ;
