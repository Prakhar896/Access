from flask import Flask, request, render_template, send_file, redirect, url_for, flash, send_from_directory
from flask_cors import CORS
import json, random, time, sys, subprocess, os, shutil
import datetime
from models import *
from certAuthority import *
from emailer import *
from dotenv import load_dotenv
load_dotenv()

### APP CONFIG
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

def allowed_file(filename):
  return ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

### Variable Creation

if not os.path.isfile('accessIdentities.txt'):
  with open('accessIdentities.txt', 'w') as f:
    f.write("{}")

accessIdentities = json.load(open('accessIdentities.txt', 'r'))

# Identity format:
# username: {
#   "password": "",
#   "email": "",
#   "sign-up-date": "",
#   "last-login-date": "",
#   "associatedCertID": "",
#   "loggedInAuthToken": "" (only present if user is logged in)
# }

if not os.path.isfile('certificates.txt'):
  with open('certificates.txt', 'w') as f:
    f_content = """{ "registeredCertificates": {}, "revokedCertificates": {}}"""
    f.write(f_content)

if not os.path.isfile('validOTPCodes.txt'):
  with open('validOTPCodes.txt', 'w') as f:
    f.write("{}")

validOTPCodes = json.load(open('validOTPCodes.txt', 'r'))

@app.route('/')
def homepage():
  return fileContent('homepage.html')

@app.route('/identity/create')
def createIdentityPage():
  return render_template('createIdentity.html')

@app.route('/identity/login/')
def loginIdentityPage():
  if 'email' not in request.args:
    return render_template('loginIdentity.html', email="")
  else:
    return render_template('loginIdentity.html', email=request.args['email'])

@app.route('/security/unauthorised')
def unauthorizedPage():
  return render_template('unauthorised.html', message=request.args['error'])

# API
from api import *

# Email OTP Service
from emailOTP import *

# Portal Service
from portal import *

# Assets
from assets import *

if __name__ == "__main__":
  response = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
  if CAError.checkIfErrorMessage(response):
    print(response)
    sys.exit(1)
  else:
    print(response)
  

  CertAuthority.expireOldCertificates()
  CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))
  tempIdentities = accessIdentities
  accessIdentities = expireAuthTokens(tempIdentities)
  json.dump(accessIdentities, open('accessIdentities.txt', 'w'))
  app.run(host='0.0.0.0', port=8000)