from flask import Flask, request, render_template, send_file
from flask_cors import CORS
import json, random, time, sys, subprocess, os, shutil
import datetime
from models import *
from certAuthority import *
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

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
#   "associatedCertID": ""
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

@app.route('/identity/login')
def loginIdentityPage():
  return render_template('loginIdentity.html')

# API
from api import *

# Email OTP Service
from emailOTP import *

# Assets
from assets import *

if __name__ == "__main__":
  response = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
  if CAError.checkIfErrorMessage(response):
    print(response)
    sys.exit(1)
  else:
    print(response)
  
  app.run(host='0.0.0.0', port=8000)