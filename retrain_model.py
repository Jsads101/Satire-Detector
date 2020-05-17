import pymysql
import sys
sys.path.append('Lib')
import string
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import os
import re
from sklearn.model_selection import train_test_split
import pickle
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
import nltk

connection = pymysql.connect(host='csmysql.cs.cf.ac.uk',
                             user='c1981660',
                             password='Hums0202020',
                             db='c1981660_Resources_Reviews',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cur = connection.cursor()

#function that gets list of txts from classificatin table
def retrieve_new_document_list():
  cur.execute("""
    SELECT text FROM classification;
    """)
  results = cur.fetchall()
  all_docs = [d['text'] for d in results]
  return all_docs

#function that gets numerical list of labels from classification table
def retrieve_labels_list():
  cur.execute("""
     SELECT category FROM classification;
     """)
  cat_results = cur.fetchall()
  all_categories = [d['category'] for d in cat_results]
  all_categories_nums = []
  for category in all_categories:
    if category == "satire":
      category = 1
      all_categories_nums.append(category)
    else:
      category = 0
      all_categories_nums.append(category)
  return all_categories_nums


#retrains model and creates new pickles for us in application
def retrain_my_model():
  print('*********Retraining Model************************')

  all_docs = retrieve_new_document_list()
  all_labels = retrieve_labels_list()

#creating test data set
  features_train, features_test, y_train, y_test = train_test_split(all_docs, all_labels, test_size = 0.2)

#creating vectorizer to identify features and change train data to numercial representations of the features
  vectorizer = TfidfVectorizer(ngram_range = (1,2))
  vectorizer.fit(all_docs)

#transforming data to umerical representations of the features
  X_train = vectorizer.transform(features_train)
  X_test = vectorizer.transform(features_test)

#creating decision tree object and training model
  clf = svm.SVC(probability=True)
  clf.fit(X_train, y_train)

#getting model to make predictions on test data set to evaluate
  predictions = clf.predict(X_test)

#model evaluations:
  #print(classification_report(y_test,predictions)) #shows the quality of predictions made by the model
  accuracy = accuracy_score(y_test, predictions) # shows how accurate the model is at predicting the correct labels for the test data set
  f1 = f1_score(y_test, predictions)

  with open('model.pkl', 'wb') as f:
    pickle.dump(clf, f)

  with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

  return accuracy, f1


if __name__ == "__main__":
  retrieve_new_document_list()
  retrieve_labels_list()
  retrain_my_model()
