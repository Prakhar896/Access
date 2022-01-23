from flask import Flask, request
from flask_cors import CORS
import json, random, time, sys, subprocess, os, shutil
import datetime

app = Flask(__name__)
CORS(app)

with open('validAuthTokens.txt', 'r') as f:
  validAuthTokens = json.load(f)

def fileContent(fileName):
  with open(fileName, 'r') as f:
    f_content = f.read()
    return f_content

def generateAuthToken():
  letters_lst = ['a', 'e', 'w', 't', 'a', 'u', 'o', 'p', '2', '5', '6', '3', '8', '4']
  authTokenString = ''
  while len(authTokenString) < 10:
    authTokenString += random.choice(letters_lst)
  return authTokenString

def checkIfPastExpiryDate(givenDatetime):
  present = datetime.datetime.now()
  isExpired = givenDatetime < present
  return isExpired

@app.route('/')
def home():
  return fileContent('homepage.html')



@app.route('/clearTokens')
def clearTokens():
  global validAuthTokens
  validAuthTokens = {}
  json.dump(validAuthTokens, open('validAuthTokens.txt', 'w'))
  return "Cleared Tokens!"

# assets
@app.route('/assets/copyright')
def copyright():
  return fileContent('copyright.js')

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8000, threaded=True)
