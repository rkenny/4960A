#!/usr/bin/python3
import pickle # for loading pickles
import cmn # for imdb data
import mysql.connector
import datetime
import os

class Database:
  movieInsertSQL = "insert into movie (id, title) values (%s, %s)"
  genreInsertSQL = "insert into genre (id, name) values (%s, %s)"
  memberInsertSQL = "insert into member (id, name) values (%s, %s)"
  movieMemberInsertSQL = "insert into movie_member (movieId, memberId) values (%s, %s)"
  genreMemberInsertSQL = "insert into genre_member (genreId, memberId) values (%s, %s)"
  genreMovieInsertSQL = "insert into genre_movie (genreId, movieId) values (%s, %s)"
  movieGenreMemberInsertSQL = "insert into movie_genre_member (movieId, genreId, memberId) values (%s, %s, %s)"
  batchSize = 10000
  uncommittedInserts = 0
  totalInserts = 0
  def __init__(self, **kwargs):
    self.dbConnection = mysql.connector.connect(host="localhost", user=kwargs['db_user'], password=kwargs['db_password'], database=kwargs['db_name'])
    self.dbCursor = self.dbConnection.cursor()
  def __del__(self):
    print("Done. " + str(self.totalInserts) + " rows inserted.")
    self.dbConnection.commit()
  def insertMovie(self, movieId, movieTitle):
    self.insert(self.movieInsertSQL, (movieId, movieTitle))
  def insertGenre(self, genreId, genreName):
    self.insert(self.genreInsertSQL, (genreId, genreName))
  def insertMember(self, memberId, memberName):
    self.insert(self.memberInsertSQL, (memberId, memberName))
  def insertMovieMember(self, movieId, memberId):
    self.insert(self.movieMemberInsertSQL, (movieId, memberId))
  def insertGenreMember(self, genreId, memberId):
    self.insert(self.genreMemberInsertSQL, (genreId, memberId))
  def insertGenreMovie(self, genreId, movieId):
    self.insert(self.genreMovieInsertSQL, (genreId, movieId))
  def insertMovieGenreMember(self, movieId, genreId, memberId):
    self.insert(self.movieGenreMemberInsertSQL, (movieId, genreId, memberId))
  def insert(self, sql, values):
    try:
      self.dbCursor.execute(sql, values)
      self.uncommittedInserts = self.uncommittedInserts + 1
      self.totalInserts = self.totalInserts + 1
      if (self.uncommittedInserts == self.batchSize):
        self.dbConnection.commit()
        self.uncommittedInserts = 0
        print("Committed at " + str(datetime.datetime.now().time()))
    except Exception as e:
      # print(e)
      pass    


def main():
  db_user = os.environ['DB_USER']
  db_pass = os.environ['DB_PASSWORD']
  db_name = os.environ['DB_NAME']
  db = Database(db_user=db_user, db_password=db_pass, db_name=db_name)
  Verbose = True
  # indexes = pickle.load(open("/mnt/4960-backup/Data/imdb/title.basics.tsv.filtered.mt5.ts2/indexes.pkl", "rb"))
  # teamsVecs = pickle.load(open("/mnt/4960-backup/Data/imdb/title.basics.tsv.filtered.mt5.ts2/teams.pkl", "rb"))
  indexes = pickle.load(open("/mnt/b_4960/Data/imdb/toy.title.basics.tsv/indexes.pkl", "rb"))
  teamsVecs = pickle.load(open("/mnt/b_4960/Data/imdb/toy.title.basics.tsv/teams.pkl", "rb"))
  for team in teamsVecs: # movieID to bundle .. that is movie.id
    bundleId = indexes["t2i"][team.id] # bundleId = indexes["t2i"][paper.id] worked for DBLP?
    for item in team.members: # team members are "items" # in imdb, they have a trailing .0 that I want to remove using int.
      itemId = indexes["c2i"][str(item.id)+"_"+item.name] # int(item.id)   # authorId = indexes["c2i"][str(author.id)+"_"+author.name] worked for DLBP?   
      print("adding " + str(item.id)+"_"+item.name)
      for skill in (team.genres+',').split(',')[:-1]: # genres are skills aka "user"... I will add a trailing , then remove the empty element to guarantee this is a list.
        genreIndex = str(indexes['s2i'][skill]) # skillIndex = str(indexes['s2i'][skill])
        db.insertMovieGenreMember(bundleId, genreIndex, itemId)
  

if __name__ == "__main__":    
  main()
