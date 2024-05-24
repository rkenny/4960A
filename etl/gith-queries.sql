
      select distinct languageId, developerId
        from repo_language_developer
into outfile '/var/lib/mysql-files/gith/user_item.txt';

     select distinct repoId, developerId
       from repo_language_developer   
into outfile '/var/lib/mysql-files/gith/bundle_item.txt';

      select distinct languageId, developerId
        from repo_language_developer
       where repoId not in (select repoId from repo_language_developer where repoId like '%__%3%3%')
into outfile '/var/lib/mysql-files/gith/user_bundle_train.txt';

      select distinct languageId, developerId
        from repo_language_developer
       where repoId in (select repoId from repo_language_developer where repoId like '%__%3%3%')
into outfile '/var/lib/mysql-files/gith/user_bundle_test.txt';

      select distinct languageId, developerId
        from repo_language_developer
       where repoId in (select repoId from repo_language_developer where repoId like '%__3%4%')
into outfile '/var/lib/mysql-files/gith/user_bundle_tune.txt';

      select sum(case when col = 'UserCount' then val else 0 end) as UserCount,
             sum(case when col = 'BundleCount' then val else 0 end) as BundleCount,
             sum(case when col = 'ItemCount' then val else 0 end) as ItemCount
        from (      select count(distinct repoId) as val, 'BundleCount' as col from repo_language_developer
              union select count(distinct languageId) as val, 'UserCount' as col from repo_language_developer
              union select count(distinct developerId) as val, 'ItemCount' as col from repo_language_developer
             ) samples
into outfile '/var/lib/mysql-files/gith/gith_data_size.txt';
