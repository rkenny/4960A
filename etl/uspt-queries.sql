
      select distinct skillId, inventorId
        from patent_skill_inventor
into outfile '/var/lib/mysql-files/uspt/user_item.txt';

     select distinct patentId, inventorId
       from patent_skill_inventor   
into outfile '/var/lib/mysql-files/uspt/bundle_item.txt';

      select distinct skillId, inventorId
        from patent_skill_inventor
       where patentId not in (select patentId from patent_skill_inventor where patentId like '%__%3%3%')
into outfile '/var/lib/mysql-files/uspt/user_bundle_train.txt';

      select distinct skillId, inventorId
        from patent_skill_inventor
       where patentId in (select patentId from patent_skill_inventor where patentId like '%__%3%3%')
into outfile '/var/lib/mysql-files/uspt/user_bundle_test.txt';

      select distinct skillId, inventorId
        from patent_skill_inventor
       where patentId in (select patentId from patent_skill_inventor where patentId like '%__3%4%')
into outfile '/var/lib/mysql-files/uspt/user_bundle_tune.txt';

      select sum(case when col = 'UserCount' then val else 0 end) as UserCount,
             sum(case when col = 'BundleCount' then val else 0 end) as BundleCount,
             sum(case when col = 'ItemCount' then val else 0 end) as ItemCount
        from (      select count(distinct patentId) as val, 'BundleCount' as col from patent_skill_inventor
              union select count(distinct skillId) as val, 'UserCount' as col from patent_skill_inventor
              union select count(distinct inventorId) as val, 'ItemCount' as col from patent_skill_inventor
             ) samples
into outfile '/var/lib/mysql-files/uspt/uspt_data_size.txt';
