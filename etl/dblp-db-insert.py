#!/usr/bin/python3
import pickle # for loading pickles
import cmn # for imdb data
import mysql.connector
import datetime
import os

class Database:
  paperInsertSQL = "insert into paper (id, title) values (%s, %s)"
  keywordInsertSQL = "insert into keyword (id, keyword) values (%s, %s)"
  authorInsertSQL = "insert into author (id, name) values (%s, %s)"
  paperAuthorInsertSQL = "insert into paper_author (paperId, authorId) values (%s, %s)"
  keywordAuthorInsertSQL = "insert into keyword_author (keywordId, authorId) values (%s, %s)"
  keywordPaperInsertSQL = "insert into keyword_paper (keywordId, paperId) values (%s, %s)"
  batchSize = 10000
  uncommittedInserts = 0
  totalInserts = 0
  def __init__(self, **kwargs):
    self.dbConnection = mysql.connector.connect(host="localhost", user=kwargs.db_user, password=kwargs.db_password, database=kwargs.db_name)
    self.dbCursor = self.dbConnection.cursor()
  def __del__(self):
    print("Done. " + str(self.totalInserts) + " rows inserted.")
    self.dbConnection.commit()
  def insertPaper(self, paperId, paperTitle):
    self.insert(self.paperInsertSQL, (paperId, paperTitle))
  def insertKeyword(self, keywordId, keyword):
    self.insert(self.keywordInsertSQL, (keywordId, keyword))
  def insertAuthor(self, authorId, authorName):
    self.insert(self.authorInsertSQL, (authorId, authorName))
  def insertPaperAuthor(self, paperId, authorId):
    self.insert(self.paperAuthorInsertSQL, (paperId, authorId))
  def insertKeywordAuthor(self, keywordId, authorId):
    self.insert(self.keywordAuthorInsertSQL, (keywordId, authorId))
  def insertKeywordPaper(self, keywordId, paperId):
    self.insert(self.keywordPaperInsertSQL, (keywordId, paperId))
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
  indexes = pickle.load(open("/mnt/b_4960/Data/dblp/dblp.v12.json.filtered.mt5.ts2/indexes.pkl", "rb"))
  teamsVecs = pickle.load(open("/mnt/b_4960/Data/dblp/dblp.v12.json.filtered.mt5.ts2/teams.pkl", "rb"))
  # indexes = pickle.load(open("/mnt/b_4960/Data/dblp/toy.dblp.v12.json/indexes.pkl", "rb"))
  # teamsVecs = pickle.load(open("/mnt/b_4960/Data/dblp/toy.dblp.v12.json/teams.pkl", "rb"))
  for paper in teamsVecs: # movieID to bundle .. that is movie.id
    print(str(paper.id) + " is a bundle. The title is: " + paper.title)
    db.insertPaper(paper.id, paper.title)
    for author in paper.members: # team members are "items" # in imdb, they have a trailing .0 that I want to remove using int.
      authorId = int(author.id)
      print(" has author " + author.name + " id("+str(author.id)+")")
      db.insertAuthor(author.id, author.name)
      db.insertPaperAuthor(paper.id, author.id)
      for skill in paper.skills:
        skillIndex = str(indexes['s2i'][skill])
        print("  with skill " + skill + " id: " + skillIndex)
        db.insertKeyword(skillIndex, skill)
        db.insertKeywordAuthor(skillIndex, authorId)
        db.insertKeywordPaper(skillIndex, paper.id)
  

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
  
