from flask import Flask, render_template, request
import pickle
import sqlite3
import os
import numpy as np
import pymysql
from model import clean_data
from model import train_model
from retrain_model import retrain_my_model


connection = pymysql.connect(host='csmysql.cs.cf.ac.uk',
                             user='c1981660',
                             password='Hums0202020',
                             db='c1981660_Resources_Reviews',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

#method which predicts category for user input
def classify(document):
  model = pickle.load(open("model.pkl", "rb")) #using pickled clf model (will be most recent version if retrained)
  vectorizer = pickle.load(open("vectorizer.pkl", "rb")) #using pickled vectorizer object (will be most recent verion if retrained)
  label_dict = {0: 'non_satire', 1: 'satire'}
  cleandocument = clean_data(document)
  X = vectorizer.transform([cleandocument])
  y = model.predict(X)[0]
  proba = np.max(model.predict_proba(X))
  return label_dict[y], proba, cleandocument


#function which moves data from user_input table to classification table before retartining the model
def update_classification_table():
  with connection.cursor() as cur:
    q = """
      INSERT INTO classification (textID, text, category) SELECT user_textID, user_text, user_category FROM user_input;
        """
    cur.execute(q)
    connection.commit()

  with connection.cursor() as cur:
    q = """
	  DELETE FROM user_input WHERE user_textID > 10885;
        """
    cur.execute(q)
    connection.commit()


#function which adds user inpit and category to the user_input table
def add_user_input_to_ui_table(document, label):
  list = [document, label]
  with connection.cursor() as cur:
    q = """
            INSERT INTO user_input(user_text, user_category) VALUES (%s, %s)
           """
    cur.execute(q, list)
    connection.commit()



#flask application code
app = Flask(__name__)


@app.route('/')
def home():
  return render_template('home.html')


@app.route('/result', methods=['POST'])
def result():
  if request.method == 'POST':
    newtext = request.form['message']
    mypred, probability, cleantext = classify(newtext)
  return render_template('result.html', content=cleantext, prediction=mypred, probability=round(probability*100, 2))


@app.route('/thanks', methods=['POST'])
def thanks():
  feedback = request.form['feedback_button']
  userinput = request.form['userinput']
  prediction = request.form['prediction']
  if (feedback == 'Incorrect') and (prediction == "satire"):
    z = "non_satire"
  elif (feedback == 'Incorrect') and (prediction == "non_satire"):
    z = "satire"
  elif (feedback == 'Correct') and (prediction == "satire"):
    z = "satire"
  elif (feedback == 'Correct') and (prediction == "non_satire"):
    z = "non_satire"
  add_user_input_to_ui_table(userinput, z)
  return render_template('thanks.html')


@app.route('/retrain', methods=['POST'])
def retrain():
 update_classification_table()
 new_accuracy, new_f1 = retrain_my_model()
 return render_template('retrained.html', accuracy = new_accuracy, f1 = new_f1)


if __name__ == '__main__':
  train_model() # runs iniial training of clf model to create model and vectorizer pickles for classifying user input
  app.run(debug=False)
