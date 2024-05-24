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
  indexes = pickle.load(open("/mnt/4960/4960_git/raw_data/imdb/toy.title.basics.tsv/indexes.pkl", "rb"))
  teamsVecs = pickle.load(open("/mnt/4960/4960_git/raw_data/imdb/toy.title.basics.tsv/teams.pkl", "rb"))
  for team in teamsVecs: # movieID to bundle .. that is movie.id
    ## print(str(team.id) + " is a bundle. The title is: " + team.o_title)
    # db.insertMovie(team.id, team.o_title)
    for item in team.members: # team members are "items" # in imdb, they have a trailing .0 that I want to remove using int.
      itemId = str(item.id) + '_' + item.name
      ## print(" has team member " + item.name + " id("+str(itemId)+")")
      # db.insertMember(itemId, item.name)
      # db.insertMovieMember(team.id, itemId)
      for skill in (team.genres+',').split(',')[:-1]: # genres are skills aka "user"... I will add a trailing , then remove the empty element to guarantee this is a list.
        genreIndex = str(indexes['s2i'][skill])
        ## print("  with skill " + skill + " id: " + genreIndex)
        # db.insertGenre(genreIndex, skill)
        # db.insertGenreMember(genreIndex, itemId)
        # db.insertGenreMovie(genreIndex, team.id)
        db.insertMovieGenreMember(indexes['t2i'][team.id], genreIndex, indexes['c2i'][itemId])
  

if __name__ == "__main__":    
  main()




   


#for bundleId in [(bundleId, str(bundleId)) for bundleId in indexes["i2t"].keys()] : # movieId to bundle ... in this case, index to title
#    print("checking bundleId " + bundleId[1] + " actual title: " + str(indexes["i2t"][bundleId[0]])) if Verbose else None
#    userIds = teamsVecs["skill"][bundleId[0]].rows[0] # genre as user for imdb ... in this case, the genre is the "skill"
#    itemIds = teamsVecs["member"][bundleId[0]].rows[0] # crew as item for imdb
#    break
    # for itemId in [(itemId, str(itemId)) for itemId in itemIds]:
    #    for userId in [(userId, str(userId)) for userId in userIds]:
    #        print(" [" + indexes["i2s"][userId[0]] + "] for [" +indexes["i2c"][itemId[0]]+ "] as ", end="") if Verbose else None
    #        print(userId[1] + " " + itemId[1])
    #        ## userItemFile.write(userId[1] + "\t" + itemId[1] + "\n")
    #        print(" [" + indexes["i2s"][userId[0]] + "] for [" +str(indexes["i2t"][bundleId[0]])+ "] as ", end="") if Verbose else None
    #        # print(userId[1] + " " + bundleId[1]) # this is the train/test set
    #        # if random.random() < testSetSize:
    #        #     userBundleTestFile.write(userId[1] + "\t" + bundleId[1] + "\n")
    #        # else:
    #        #     userBundleTrainFile.write(userId[1] + "\t" + bundleId[1] + "\n")
    #    print(" [" + str(indexes["i2t"][bundleId[0]]) +"] has crew " + indexes["i2c"][bundleId[0]] + " as ", end="") if Verbose else None
    #    # print(bundleId[1] + " " + itemId[1])
    #    # bundleItemFile.write(bundleId[1] + "\t" + itemId[1] + "\n")
  
