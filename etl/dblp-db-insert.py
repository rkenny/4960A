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
  keywordPaperKeywordAuthorSQL = "insert into paper_keyword_author (paperId, keywordId, authorId) values (%s, %s, %s)"
  batchSize = 10000
  uncommittedInserts = 0
  totalInserts = 0
  def __init__(self, **kwargs):
    print(kwargs)
    self.dbConnection = mysql.connector.connect(host="localhost", user=kwargs['db_user'], password=kwargs['db_password'], database=kwargs['db_name'])
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
  def insertPaperKeywordAuthor(self, paperId, skillIndex, authorId):
    self.insert(self.keywordPaperKeywordAuthorSQL, (paperId, skillIndex, authorId))
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
  print("Loading indexes pickle.")
  indexes = pickle.load(open("/mnt/4960/4960_git/raw_data/dblp/dblp.v12.json.filtered.mt75.ts3/indexes.pkl", "rb"))
  print("Done with indexes.")
  print("Loading teams pickle.")
  teamsVecs = pickle.load(open("/mnt/4960/4960_git/raw_data/dblp/dblp.v12.json.filtered.mt75.ts3/teams.pkl", "rb"))
  print("Done with teams.")
  # indexes = pickle.load(open("/mnt/b_4960/Data/dblp/toy.dblp.v12.json/indexes.pkl", "rb"))
  # teamsVecs = pickle.load(open("/mnt/b_4960/Data/dblp/toy.dblp.v12.json/teams.pkl", "rb"))
  for paper in teamsVecs: # movieID to bundle .. that is movie.id
    bundleId = indexes["t2i"][paper.id]
    ### db.insertPaper(bundleId, paper.title)
    for author in paper.members: # team members are "items" # in imdb, they have a trailing .0 that I want to remove using int.
      authorId = indexes["c2i"][str(author.id)+"_"+author.name]
      ### db.insertAuthor(authorId, author.name)
      ###db.insertPaperAuthor(bundleId, authorId)
      for skill in paper.skills:
        skillIndex = str(indexes['s2i'][skill])
        ###db.insertKeyword(skillIndex, skill)
        ###db.insertKeywordAuthor(skillIndex, authorId)
        ### db.insertKeywordPaper(skillIndex, bundleId)
        print(str(paper.id) + " " + str(skillIndex) + " " + str(authorId))
        db.insertPaperKeywordAuthor(bundleId, skillIndex, authorId)
  

if __name__ == "__main__":    
  main()

