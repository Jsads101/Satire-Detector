import sys
sys.path.append('Lib')
import string
from nltk.corpus import stopwords
from sklearn import tree
from collections import Counter
import os
import pymysql
import re

connection = pymysql.connect(host='csmysql.cs.cf.ac.uk',
                             user='c1981660',
                             password='Hums0202020',
                             db='c1981660_Resources_Reviews',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


#function that cleans strings for special characters, multiple spaces and single characters
def clean_data(text):
  document = re.sub(r'\W', ' ', text)
  document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
  document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)
  document = re.sub(r'\s+', ' ', document, flags=re.I)
  #document = [word for word in document.split() if word.lower() not in stopwords.words("english")]
  #final_document = " ".join(document)
  return document

def get_text_list(file):
  list_of_texts = []
  seperate_texts = file.split('\n')
  for line in seperate_texts:
    clean_line = clean_data(line)
    list_of_texts.append(clean_line)
  return list_of_texts


#function  thats reads data folder and creates dictionary where keys = "pos" and "neg" and values are a list of lists (where one review = a list of strings)
def load_data(data_folder):
  d={}
  files = os.listdir(data_folder)
  for infile in files:
    f = open(os.path.join(data_folder,infile), encoding="utf8")
    data = f.read()
    list_of_texts = get_text_list(data)
    d[infile] = list_of_texts
  return d


#Methods to create and populate table

def create_tables():
  with connection.cursor() as cur:
    q = """
	  CREATE TABLE classification(
	  textID INT UNSIGNED NOT NULL,
	  text VARCHAR(350) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
      category VARCHAR(24),
	  PRIMARY KEY (textID)
	  );
		"""
    cur.execute(q)
    connection.commit()

  with connection.cursor() as cur:
    q = """
 	  CREATE TABLE user_input(
 	  user_textID INT AUTO_INCREMENT,
 	  user_text VARCHAR(350) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
      user_category VARCHAR(24),
 	  PRIMARY KEY (user_textID)
 	  );
 		"""
    cur.execute(q)
    connection.commit()

  with connection.cursor() as cur:
    q = """
 	  ALTER TABLE user_input AUTO_INCREMENT=10886;
 		"""
    cur.execute(q)
    connection.commit()


def populate_classification(text_list_1, text_list_2):
  text_list = []
  textID = 1
  for text in text_list_1:
      if (len(text) != 0):
        new_list = [textID, text, "satire"]
        text_list.append(new_list)
        textID = textID + 1

  for text in text_list_2:
      if (len(text) != 0):
        new_list = [textID, text, "non_satire"]
        text_list.append(new_list)
        textID = textID + 1

  with connection.cursor() as cur:
    q = """
         INSERT INTO classification(textID, text, category) VALUES (%s, %s, %s)
        """
    cur.executemany(q, text_list)
    connection.commit()



data_dict = load_data("satire") # create dictionary from data file to populate tables (only mmost frequent words)

try:
  print('creating classification and user_input tables')
  create_tables()
  print('populating the classification and user_input tables')
  populate_classification(data_dict["satire"], data_dict["non_satre"])

finally:
  connection.close()
