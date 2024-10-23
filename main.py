from bootCheck import runBootCheck
if __name__ == "__main__":
    if not runBootCheck():
        print("MAIN: Boot check failed. Boot aborted.")
        exit()

import json, random, time, sys, subprocess, os, shutil, copy, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from werkzeug.utils import secure_filename
from flask_cors import CORS
from models import *
from config import Config
from activation import *
from AFManager import *
from emailer import *
from accessAnalytics import *
from getpass import getpass

### APP CONFIG
configManager = Config()

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Chute')
readableFileExtensions = ', '.join(["."+x for x in configManager.config["fileExtensions"]])

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = configManager.config["allowedFileSize"] * 1000 * 1000
app.secret_key = os.environ['APP_SECRET_KEY']

def allowed_file(filename):
    return ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in configManager.config["fileExtensions"])

## Other pre-requisites
@app.before_request
def updateAnalytics():
    if AccessAnalytics.permissionCheck():
        response = AccessAnalytics.newRequest(request.path)
        if isinstance(response, str):
            if response.startswith("AAError:"):
                print(response)
        
        if request.method == "POST":
            postResponse = AccessAnalytics.newPOSTRequest()
            if isinstance(postResponse, str):
                if postResponse.startswith("AAError:"):
                    print(postResponse)
  

@app.route('/')
def homepage():
    return 'A better Access is coming soon.'

@app.route('/version')
def version():
    if Universal.version == None:
        num = Universal.getVersion()
        if num == "Version File Not Found":
            num = "Version information could not be obtained."
    else:
        num = Universal.version

    return render_template('version.html', versionNum=num)

if __name__ == "__main__":
    # New bootloading coming soon
    
    port = os.environ.get('RuntimePort', 8000)
    app.run(host='0.0.0.0', port=port)