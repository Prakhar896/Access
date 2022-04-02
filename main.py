from flask import Flask, request, render_template, send_file, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
import json, random, time, sys, subprocess, os, shutil
import datetime
from models import *
from certAuthority import *
from AFManager import *
from emailer import *
from accessAnalytics import *
from dotenv import load_dotenv
load_dotenv()

### APP CONFIG
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Chute')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = os.environ['APP_SECRET_KEY']

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

if not os.path.isdir(os.path.join(os.getcwd(), 'AccessFolders')):
  os.mkdir(os.path.join(os.getcwd(), 'AccessFolders'))

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

@app.route('/identity/logout/')
def logout():
  if 'username' not in request.args:
    flash('Username was not provided for identity logout. Failed to perform identity logout.')
    return redirect(url_for('processError'))
  elif 'authToken' not in request.args:
    flash('Authentication token was not provided for identity logout. Failed to perform identity logout.')
    return redirect(url_for('processError'))
  return render_template('logout.html', username=request.args['username'])

@app.route('/security/unauthorised')
def unauthorizedPage():
  return render_template('unauthorised.html', message=request.args['error'])

@app.route('/security/error')
def processError():
  if 'error' not in request.args:
    return render_template('error.html', error=None)
  else:
    return render_template('error.html', error=request.args['error'])

# API
from api import *

# Email OTP Service
from emailOTP import *

# Portal Service
from portal import *

# Assets
from assets import *

if __name__ == "__main__":
  # Load certificates
  CAresponse = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
  if CAError.checkIfErrorMessage(CAresponse):
    print(CAresponse)
    sys.exit(1)
  else:
    print(CAresponse)
  
  # Expire old certificates and save new data
  CertAuthority.expireOldCertificates()
  CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))

  ## Expire auth tokens
  tempIdentities = accessIdentities
  accessIdentities = expireAuthTokens(tempIdentities)
  json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

  ## Set up Access Analytics
  if AccessAnalytics.permissionCheck():
    AAresponse = AccessAnalytics.prepEnvironmentForAnalytics()
    if AAresponse.startswith("AAError:"):
      print("MAIN: Error in getting Analytics to prep environment. Response: {}".format(AAresponse))
      sys.exit(1)
    elif AAresponse != "AA: Environment prep successful.":
      print("MAIN: Unknown response when attempting to get Analytics to prep environment. Response: {}".format(AAresponse))
      sys.exit(1)
    else:
      print(AAresponse)
  else:
    print("MAIN: Notice!!! AccessAnalytics is not enabled and will not be setup and run.")

  ## Port check
  if 'RuntimePort' not in os.environ:
    print("MAIN: RuntimePort environment variable is not set in .env file. Access cannot be booted without a valid port set. Please re-boot Access after setting RuntimePort.")
    sys.exit(1)
  elif not os.environ['RuntimePort'].isdigit():
    print("MAIN: RuntimePort environment variable has an invalid value. Port value must be an integer.")
    sys.exit(1)
      
  print("All services are online; boot pre-processing and setup completed.")
  print()
  print("Booting Access...")
  print()
  app.run(host='0.0.0.0', port=int(os.environ['RuntimePort']))