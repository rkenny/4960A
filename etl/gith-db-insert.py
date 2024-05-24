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
  repoInsertSQL = "insert into repo (id, name) values (%s, %s)"
  languageInsertSQL = "insert into language (id, language) values (%s, %s)"
  developerInsertSQL = "insert into developer (id, name) values (%s, %s)"
  
  repoDeveloperInsertSQL = "insert into repo_developer (repoId, developerId) values (%s, %s)"
  languageDeveloperInsertSQL = "insert into language_developer (languageId, developerId) values (%s, %s)"
  languageRepoInsertSQL = "insert into language_repo (languageId, repoId) values (%s, %s)"
  languageRepoDeveloperSQL = "insert into repo_language_developer (repoId, languageId, developerId) values (%s, %s, %s)"

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
  def insertRepo(self, repoId, repoTitle):
    self.insert(self.repoInsertSQL, (repoId, repoTitle))
  def insertLanguage(self, languageId, language):
    self.insert(self.languageInsertSQL, (languageId, language))
  def insertDeveloper(self, developerId, developerName):
    self.insert(self.developerInsertSQL, (developerId, developerName))
  def insertRepoDeveloper(self, repoId, developerId):
    self.insert(self.repoDeveloperInsertSQL, (repoId, developerId))
  def insertLanguageDeveloper(self, languageId, developerId):
    self.insert(self.languageDeveloperInsertSQL, (languageId, developerId))
  def insertLanguageRepo(self, languageId, repoId):
    self.insert(self.languageRepoInsertSQL, (languageId, repoId))
  def insertRepoLanguageDeveloper(self, repoId, languageId, developerId):
    self.insert(self.languageRepoDeveloperSQL, (repoId, languageId, developerId))
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
  indexes = pickle.load(open("/mnt/4960/4960_git/raw_data/gith/data.csv.filtered.mt75.ts3/indexes.pkl", "rb"))
  indexes['s2i']['none']=20 # added for the few repos that had no skills
  print("Done with indexes.")
  print("Loading teams pickle.")
  teamsVecs = pickle.load(open("/mnt/4960/4960_git/raw_data/gith/data.csv.filtered.mt75.ts3/teams.pkl", "rb"))
  print("Done with teams.")
  for repo in teamsVecs: # movieID to bundle .. that is movie.id
    repoId = indexes["t2i"][repo.id]
    ### db.insertPaper(bundleId, paper.title)
    for developer in repo.members: # team members are "items" # in imdb, they have a trailing .0 that I want to remove using int.
      developerId = indexes["c2i"][str(developer.id)+"_"+developer.name]
      ### db.insertAuthor(authorId, author.name)
      ###db.insertPaperAuthor(bundleId, authorId)
      if len(repo.skills) == 0:
        repo.skills.add('none')
      for language in repo.skills:
        languageIndex = str(indexes['s2i'][language])
        ###db.insertKeyword(skillIndex, skill)
        ###db.insertKeywordAuthor(skillIndex, authorId)
        ### db.insertKeywordPaper(skillIndex, bundleId)
        print(str(repoId) + " " + str(languageIndex) + " " + str(developerId))
        db.insertRepoLanguageDeveloper(repoId, languageIndex, developerId)
  

if __name__ == "__main__":    
  main()
