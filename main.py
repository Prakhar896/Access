from flask import Flask, request
from flask_cors import CORS
import json, random, time, sys, subprocess, os, shutil
import datetime
from models import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
  return fileContent('homepage.html')

# Assets
from assets import *

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8000, threaded=True)
