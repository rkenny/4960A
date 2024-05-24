#!/usr/bin/python3
import pickle # for loading pickles
import cmn # for imdb data
import mysql.connector
import datetime
import os

class Database:
  # paperInsertSQL = "insert into paper (id, title) values (%s, %s)"
  # keywordInsertSQL = "insert into keyword (id, keyword) values (%s, %s)"
  # authorInsertSQL = "insert into author (id, name) values (%s, %s)"
  # keywordAuthorInsertSQL = "insert into keyword_author (keywordId, authorId) values (%s, %s)"
  # keywordPaperInsertSQL = "insert into keyword_paper (keywordId, paperId) values (%s, %s)"
  # paperAuthorInsertSQL = "insert into paper_author (paperId, authorId) values (%s, %s)"
  # keywordPaperKeywordAuthorSQL = "insert into paper_keyword_author (paperId, keywordId, authorId) values (%s, %s, %s)"
  patentInsertSQL = "insert into patent (id, name) values (%s, %s)"
  skillInsertSQL = "insert into skill (id, skill) values (%s, %s)"
  inventorInsertSQL = "insert into inventor (id, name) values (%s, %s)"
  
  patentInventorInsertSQL = "insert into patent_inventor (patentId, inventorId) values (%s, %s)"
  skillInventorInsertSQL = "insert into skill_inventor (skillId, inventorId) values (%s, %s)"
  skillPatentInsertSQL = "insert into skill_patent (skillId, patentId) values (%s, %s)"
  patentSkillInventorSQL = "insert into patent_skill_inventor (patentId, skillId, inventorId) values (%s, %s, %s)"

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
  def insertPatent(self, patentId, patentTitle):
    self.insert(self.patentInsertSQL, (patentId, patentTitle))
  def insertSkill(self, skillId, skill):
    self.insert(self.skillInsertSQL, (skillId, skill))
  def insertInventor(self, inventorId, inventorName):
    self.insert(self.inventorInsertSQL, (inventorId, inventorName))
  def insertPatentInventor(self, patentId, inventorId):
    self.insert(self.patentInventorInsertSQL, (patentId, inventorId))
  def insertSkillInventor(self, skillId, inventorId):
    self.insert(self.skillInventorInsertSQL, (skillId, inventorId))
  def insertSkillPatent(self, skillId, inventorId):
    self.insert(self.skillPatentInsertSQL, (skillId, patentId))
  def insertPatentSkillInventor(self, patentId, skillId, inventorId):
    self.insert(self.patentSkillInventorSQL, (patentId, skillId, inventorId))
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
  indexes = pickle.load(open("/mnt/4960/4960_git/raw_data/uspt/patent.tsv.filtered.mt75.ts3/indexes.pkl", "rb"))
  # indexes['s2i']['none']=20 # added for the few repos that had no skills
  print("Done with indexes.")
  print("Loading teams pickle.")
  teamsVecs = pickle.load(open("/mnt/4960/4960_git/raw_data/uspt/patent.tsv.filtered.mt75.ts3/teams.pkl", "rb"))
  print("Done with teams.")
  for patent in teamsVecs: # movieID to bundle .. that is movie.id
    patentId = indexes["t2i"][patent.id]
    ### db.insertPaper(bundleId, paper.title)
    for inventor in patent.members: # team members are "items" # in imdb, they have a trailing .0 that I want to remove using int.
      inventorId = indexes["c2i"][str(inventor.id)+"_"+inventor.name]
      ### db.insertAuthor(authorId, author.name)
      ###db.insertPaperAuthor(bundleId, authorId)
      #if len(repo.skills) == 0:
      #  repo.skills.add('none')
      for skill in patent.skills:
        skillIndex = str(indexes['s2i'][skill])
        ###db.insertKeyword(skillIndex, skill)
        ###db.insertKeywordAuthor(skillIndex, authorId)
        ### db.insertKeywordPaper(skillIndex, bundleId)
        print(str(patentId) + " " + str(skillIndex) + " " + str(inventorId))
        db.insertPatentSkillInventor(patentId, skillIndex, inventorId)
  

if __name__ == "__main__":    
  main()
