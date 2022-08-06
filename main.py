from flask import Flask, request, render_template, send_file, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
import json, random, time, sys, subprocess, os, shutil, copy
import datetime
from dotenv import load_dotenv
load_dotenv()
from models import *
from certAuthority import *
from AFManager import *
from emailer import *
from accessAnalytics import *
from getpass import getpass

### APP CONFIG
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Chute')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'mov', 'mp4'}
ALLOWED_EXTENSIONS_AS_LIST = [x for x in ALLOWED_EXTENSIONS]
prepFileExtensions = ', '.join(["."+x for x in ALLOWED_EXTENSIONS_AS_LIST])

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = os.environ['APP_SECRET_KEY']

devMode = False
if 'DeveloperModeEnabled' in os.environ and os.environ['DeveloperModeEnabled'] == 'True':
  devMode = True


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
  return render_template('unauthorised.html', message=request.args['error'], originURL=request.host_url)

@app.route('/security/error')
def processError():
  if 'error' not in request.args:
    return render_template('error.html', error=None, originURL=request.host_url)
  else:
    return render_template('error.html', error=request.args['error'], originURL=request.host_url)

@app.route('/certManagement/renewal')
def renewCertificate():
  if not os.path.isfile(os.path.join(os.getcwd(), 'authorisation.txt')):
    flash('No boot authorisation code is set in the system. Certificate renewal cannot occur without a boot authorisation code being set.')
    return redirect(url_for('processError'))

  if 'certID' not in request.args or 'bootAuthCode' not in request.args:
    flash('One or more required request arguments were not present.')
    return redirect(url_for('processError'))

  if request.args['bootAuthCode'] != CertAuthority.decodeFromB64(fileContent('authorisation.txt')):
    return render_template('unauthorised.html', message='Provided boot authorisation code is incorrect.', originURL=request.host_url)

  response = CertAuthority.renewCertificate(request.args['certID'])
  if CAError.checkIfErrorMessage(response):
    flash(response)
    return redirect(url_for('processError'))

  if response == "Successfully renewed certificate with ID: {}".format(request.args['certID']):
    # Success case
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))
    return render_template('renewSuccess.html', originURL=request.host_url, certID=request.args['certID'])
  else:
    flash("Unknown response received from CertAuthority when renewing. Response: {}".format(response))
    return redirect(url_for('processError'))

@app.route('/version')
def version():
  num = 'Error in reading version data.'
  try:
    with open('version.txt', 'r') as f:
      num = f.read()
  except Exception as e:
    print("MAIN: Error in reading version data from version.txt file when request was made to /version endpoint. Error:", e)

  return render_template('version.html', versionNum=num)

# API
from api import *

# Email OTP Service
from emailOTP import *

# Portal Service
from portal import *

# Assets
from assets import *

def bootFunction():
  # BOOT PRE-PROCESSING
  global accessIdentities
  global validOTPCodes

  # Boot Authorisation
  if os.path.isfile(os.path.join(os.getcwd(), 'authorisation.txt')):
    try:
      with open('authorisation.txt', 'r') as f:
        decoded = CertAuthority.decodeFromB64(f.read())
        code = getpass("MAIN: Enter your Boot Authorisation Code to begin Access Boot: ")
        if code != decoded:
          print("MAIN: Boot Authorisation Code is incorrect. Main will not proceed with the boot.")
          sys.exit(1)
        else:
          print()
    except Exception as e:
      print("MAIN: Failed to load and ask for boot authorisation code. Error: {}".format(e))
      print("MAIN: Main will not proceed with the boot.")
      sys.exit(1)

  # Check if system is in beta mode
  if not os.path.isfile(os.path.join(os.getcwd(), 'version.txt')):
    print("MAIN: Unable to check system version! (version.txt file not present) Will ignore and attempt to proceed with boot.")
  else:
    with open('version.txt', 'r') as f:
      fileData = f.read()
      if fileData.endswith("beta"):
        print("MAIN: Note! You are booting a version of Access that is in beta! Version Info: '" + fileData + "'")
      else:
        print("MAIN: Boot version detected: '" + fileData + "'")

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
  tempIdentities = copy.deepcopy(accessIdentities)
  accessIdentities = expireAuthTokens(tempIdentities)
  json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

  # Run code that supports older versions (Backwards compatibility)
  report = []

  ## SUPPORT FOR v1.0.2
  for username in accessIdentities:
    if 'settings' not in accessIdentities[username] or ('emailPref' not in accessIdentities[username]['settings']):
      report.append('Settings data including email preferences were added to user \'{}\''.format(username))
      accessIdentities[username]['settings'] = {
            "emailPref": {
                "loginNotifs": True,
                "fileUploadNotifs": False,
                "fileDeletionNotifs": False
            }
        }

    if 'folderRegistered' not in accessIdentities[username]:
      report.append('Folder registration status data was added to user \'{}\''.format(username))
      if AFManager.checkIfFolderIsRegistered(username):
        accessIdentities[username]['folderRegistered'] = True
      else:
        accessIdentities[username]['folderRegistered'] = False
    
    if 'AF_and_files' not in accessIdentities[username]:
      accessIdentities[username]['AF_and_files'] = {}
      report.append('AF Files data was added to user \'{}\''.format(username))
      if AFManager.checkIfFolderIsRegistered(username):
        currentDatetimeString = datetime.datetime.now().strftime(systemWideStringDateFormat)
        
        for filename in AFManager.getFilenames(username):
          accessIdentities[username]['AF_and_files'][filename] = currentDatetimeString

    ## SUPPORT FOR v1.0.3
    for username in CertAuthority.registeredCertificates:
      if 'user' not in CertAuthority.registeredCertificates[username]:
        report.append("'user' parameter was added to unrevoked certificate of identity with username {}".format(username))
        CertAuthority.registeredCertificates[username]['user'] = username
    for username in CertAuthority.revokedCertificates:
      if 'user' not in CertAuthority.revokedCertificates[username]:
        report.append("'user' parameter was added to revoked certificate of identity with username {}".format(username))
        CertAuthority.revokedCertificates[username]['user'] = username
    
    CertAuthority.saveCertificatesToFile(fileObject=open('certificates.txt', 'w'))
        
  json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

  if len(report) != 0:
    print()
    print("BACKWARDS COMPATIBILITY (BC) code made the following changes:")
    for item in report:
      print('\t' + item)
    print()

  ## Set up Access Analytics
  if AccessAnalytics.permissionCheck():
    AAresponse = AccessAnalytics.prepEnvironmentForAnalytics()
    if AAresponse.startswith("AAError:"):
      print("MAIN: Error in getting Analytics to prep environment. Response: {}".format(AAresponse))
      print()
      print("MAIN: Would you like to enable Analytics Recovery Mode?")
      recoveryModeAction = input("Type 'yes' or 'no': ")
      if recoveryModeAction == "yes":
        AccessAnalytics.analyticsRecoveryMode()
      elif recoveryModeAction == "no":
        print("MAIN: Recovery mode was not enabled. Access Boot is aborted.")
        sys.exit(1)
      else:
        print("MAIN: Invalid action provided. Access Boot is aborted.")
        sys.exit(1)
    elif AAresponse != "AA: Environment prep successful.":
      print("MAIN: Unknown response when attempting to get Analytics to prep environment. Response: {}".format(AAresponse))
      print()
      print("MAIN: Would you like to enable Analytics Recovery Mode?")
      recoveryModeActionTwo = input("Type 'yes' or 'no': ")
      if recoveryModeActionTwo == "yes":
        AccessAnalytics.analyticsRecoveryMode()
      elif recoveryModeActionTwo == "no":
        print("MAIN: Recovery mode was not enabled. Access Boot is aborted.")
        sys.exit(1)
      else:
        print("MAIN: Invalid action provided. Access Boot is aborted.")
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

  # app.config['SERVER_NAME'] = 'prakhar.com:' + os.environ['RuntimePort']
  app.run(host='0.0.0.0', debug=False, port=int(os.environ['RuntimePort']))

if __name__ == "__main__":
  bootFunction()