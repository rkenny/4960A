-- create database toy_imdb;
-- use toy_imdb;

-- create table movie_genre_member (
--  genreId varchar(25),
--   memberId varchar(25),
--  movieId varchar(25)
-- );



      select distinct genreId, memberId
        from movie_genre_member
into outfile '/var/lib/mysql-files/imdb-toy/user_item.txt';

     select distinct movieId, memberId
       from movie_genre_member   
into outfile '/var/lib/mysql-files/imdb-toy/bundle_item.txt';

      select distinct genreId, movieId
        from movie_genre_member
into outfile '/var/lib/mysql-files/imdb-toy/user_bundle_train.txt';

      select distinct movie_genre_member.genreId, movie_genre_member.movieId
        from movie_genre_member
into outfile '/var/lib/mysql-files/imdb-toy/user_bundle_test.txt';

      select distinct genreId, movieId
        from movie_genre_member
into outfile '/var/lib/mysql-files/imdb-toy/user_bundle_tune.txt';

      select sum(case when col = 'UserCount' then val else 0 end) as UserCount,
             sum(case when col = 'BundleCount' then val else 0 end) as BundleCount,
             sum(case when col = 'ItemCount' then val else 0 end) as ItemCount
        from (      select count(distinct movieId) as val, 'BundleCount' as col from movie_genre_member
              union select count(distinct genreId) as val, 'UserCount' as col from movie_genre_member
              union select count(distinct memberId) as val, 'ItemCount' as col from movie_genre_member
             ) samples
into outfile '/var/lib/mysql-files/imdb-toy/imdb_data_size.txt';
