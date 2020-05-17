import sys
sys.path.append('Lib')
import string
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import os
from collections import Counter
import re
from sklearn.model_selection import train_test_split
import pickle
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
import nltk



#function that cleans strings for special characters, multiple spaces and single characters
def clean_data(text):
  document = re.sub(r'\W', ' ', text)
  document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
  document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)
  document = re.sub(r'\s+', ' ', document, flags=re.I)
  return document

#reads data in files and converts to python dictionary
def load_data(data_folder):
  d={}
  files = os.listdir(data_folder)
  for infile in files:
    f = open(os.path.join(data_folder,infile), encoding="utf8")
    data = f.read()
    seperate_texts = data.split('\n')
    list_of_clean_texts = []
    for text in seperate_texts:
      clean_text = clean_data(text)
      list_of_clean_texts.append(clean_text)
    d[infile] = list_of_clean_texts
  return d


def train_model():

  print('*******Training Initial Model************')
  data = load_data("satire")
  all_docs = data["satire"] + data["non_satre"]
  all_labels = [1 for x in data["satire"]]+[0 for x in data["non_satre"]]

#creating test data set
  features_train, features_test, y_train, y_test = train_test_split(all_docs, all_labels, test_size = 0.3)

#creating vectorizer to identify features
  vectorizer = TfidfVectorizer(ngram_range = (1,2))
  vectorizer.fit(all_docs)

#transforming data to numerical representations of the features
  X_train = vectorizer.transform(features_train)
  X_test = vectorizer.transform(features_test)

#creating algorothm object and training the model
  clf = svm.SVC(kernel='linear', probability=True)
  clf.fit(X_train, y_train)

  pickle.dump(vectorizer, open('vectorizer.pkl', 'wb')) # saves vectorizer to pickle so that it can be used again
  pickle.dump(clf, open('model.pkl', 'wb')) # saves clf model to pickle so it can be used again

def train_model():
  print('*******Training Initial Model************')
  data = load_data("satire")
  all_docs = data["satire"] + data["non_satre"]
  all_labels = [1 for x in data["satire"]]+[0 for x in data["non_satre"]]

#creating test data set
  features_train, features_test, y_train, y_test = train_test_split(all_docs, all_labels, test_size = 0.3)

#creating vectorizer to identify features
  vectorizer = TfidfVectorizer(ngram_range = (1,2))
  vectorizer.fit(all_docs)

#transforming data to numerical representations of the features
  X_train = vectorizer.transform(features_train)
  X_test = vectorizer.transform(features_test)

#creating algorothm object and training the model
  clf = svm.SVC(kernel='linear', probability=True)
  clf.fit(X_train, y_train)

  pickle.dump(vectorizer, open('vectorizer.pkl', 'wb')) # saves vectorizer to pickle so that it can be used again
  pickle.dump(clf, open('model.pkl', 'wb')) # saves clf model to pickle so it can be used again


train_my_model()
