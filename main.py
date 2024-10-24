from bootCheck import runBootCheck
if __name__ == "__main__":
    if not runBootCheck():
        print("MAIN: Boot check failed. Boot aborted.")
        exit()

import json, random, time, sys, subprocess, os, shutil, copy
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from werkzeug.utils import secure_filename
from flask_cors import CORS
import datetime
from models import *
from config import Config
from activation import *
from certAuthority import *
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

### Variable Creation

if not os.path.isfile(os.path.join(os.getcwd(), 'accessIdentities.txt')):
    with open('accessIdentities.txt', 'w') as f:
        f.write("{}")

accessIdentities = json.load(open('accessIdentities.txt', 'r'))

if not os.path.isfile(os.path.join(os.getcwd(), 'certificates.txt')):
    with open('certificates.txt', 'w') as f:
        f_content = """{ "registeredCertificates": {}, "revokedCertificates": {}}"""
        f.write(f_content)

if not os.path.isfile(os.path.join(os.getcwd(), 'validOTPCodes.txt')):
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
    return render_template('homepage.html')

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

    if request.args['bootAuthCode'] != Encryption.decodeFromB64(fileContent('authorisation.txt')):
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
    if Universal.version == None:
        num = Universal.getVersion()
        if num == "Version File Not Found":
            num = "Version information could not be obtained."
    else:
        num = Universal.version

    return render_template('version.html', versionNum=num)

def bootFunction():
    # BOOT PRE-PROCESSING
    global accessIdentities
    global validOTPCodes

    # Setup Logger service
    Logger.setup()

    # Boot Authorisation
    if os.path.isfile(os.path.join(os.getcwd(), 'authorisation.txt')):
        try:
            with open('authorisation.txt', 'r') as f:
                decoded = Encryption.decodeFromB64(f.read())
                code = getpass("MAIN: Enter your Boot Authorisation Code to begin Access Boot: ")
                if code != decoded:
                    print("MAIN: Boot Authorisation Code is incorrect. Aborting boot.")
                    Logger.log("MAIN BOOT: Aborting due to incorrect boot auth code.")
                    sys.exit(1)
                else:
                    print()
        except Exception as e:
            Logger.log("MAIN BOOT: Aborting due to loading of and prompting for boot auth code; error: {}".format(e))
            print("MAIN: Failed to load and ask for boot authorisation code.")
            print("MAIN: Aborting boot.")
            sys.exit(1)

    # Check if system is in beta mode
    versionLookup = Universal.getVersion()
    if versionLookup == "Version File Not Found":
        print("MAIN: Version file was not found. Boot aborted. Please re-install Access.")
        Logger.log("MAIN BOOT: Aborting due to missing version file.")
        sys.exit(1)
    elif versionLookup.endswith("beta"):
        print("MAIN: Note! You are booting a version of Access that is in beta! Version Info: '" + versionLookup + "'")
    else:
        print("MAIN: Boot version detected: '" + versionLookup + "'")

    # Check for copy activation (Activator DRM Process)
    activationCheck = checkForActivation()
    if activationCheck == True:
        print("MAIN-ACTIVATOR: Access copy is activated!")
    elif activationCheck == False:
        print("MAIN: Access copy is not activated! Triggering copy activation process...")
        print()
        try:
            initActivation("z44bzvw0", Universal.version)
            Logger.log("MAIN BOOT: Activated copy and obtained license key.")
        except Exception as e:
            print("MAIN ERROR: An error occurred in activating this copy. Error: {}".format(e))
            print("MAIN: Boot aborted.")
            Logger.log("MAIN BOOT: Activation error occurred: {}".format(e))
            sys.exit(1)
    else:
        # KVR
        print("MAIN: This copy's license key needs to be verified (every 14 days). Triggering key verification request...")
        print()
        try:
            makeKVR("z44bzvw0", Universal.version)
            Logger.log("MAIN BOOT: Completed a KVR successfully.")
        except Exception as e:
            print("MAIN ERROR: Failed to make KVR request. Error: {}".format(e))
            print("MAIN: Boot aborted.")
            sys.exit(1)
    print()

    # Run code that supports older versions (Backwards compatibility)
    report = []

    ## SUPPORT FOR v1.0.3
    if os.environ.get("ReplitEnvironment", "nil") != "nil":
        print("MAIN NOTICE: Detection of Replit environment with ReplitEnvironment .env variable was deprecated in v1.0.4. Refer to documentation for more information.")
        print()

    for username in accessIdentities:
        ## Check if password is in old base64 format
        if Encryption.isBase64(accessIdentities[username]["password"]):
            accessIdentities[username]["password"] = Encryption.convertBase64ToSHA(accessIdentities[username]["password"])
            report.append("Password in old Base64 format for user '{}' has been updated to a more secure format.".format(username))

        if ("identityVersion" not in accessIdentities[username]) or (accessIdentities[username]["identityVersion"] != Universal.version):
            accessIdentities[username]["identityVersion"] = Universal.version
            report.append("Updated identity version for user '{}' to '{}'".format(username, Universal.version))

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
                currentDatetimeString = datetime.datetime.now().strftime(Universal.systemWideStringDateFormat)
                
                for filename in AFManager.getFilenames(username):
                    accessIdentities[username]['AF_and_files'][filename] = currentDatetimeString
            
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

    if len(report) != 0:
        print()
        print("BACKWARDS COMPATIBILITY (BC) code made the following changes:")
        for item in report:
            print('\t' + item)
            print()

    # Load certificates
    CAresponse = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
    if CAError.checkIfErrorMessage(CAresponse):
        Logger.log("MAIN BOOT: Failed to make CA load certificates; response: {}".format(CAresponse))
        print("MAIN: Failed to load certificates from file. Please try again.")
        sys.exit(1)
    else:
        print(CAresponse)
    
    # Expire old certificates and save new data
    CertAuthority.expireOldCertificates()
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))

    # Expire auth tokens
    tempIdentities = accessIdentities
    accessIdentities = expireAuthTokens(tempIdentities)
    with open('accessIdentities.txt', 'w') as f:
        json.dump(accessIdentities, f)

    # Set up Access Analytics
    if AccessAnalytics.permissionCheck():
        AAresponse = AccessAnalytics.prepEnvironmentForAnalytics()
        if AAresponse.startswith("AAError:"):
            print("MAIN: Error in getting Analytics to prep environment. Response: {}".format(AAresponse))
            print()
            print("MAIN: Would you like to enable Analytics Recovery Mode?")
            recoveryModeAction = input("Type 'yes' or 'no': ")
            if recoveryModeAction == "yes":
                Logger.log("MAIN BOOT: Access Analytics Recovery Mode was activated.")
                AccessAnalytics.analyticsRecoveryMode()
            elif recoveryModeAction == "no":
                print("MAIN: Recovery mode was not enabled. Access Boot is aborted.")
                Logger.log("MAIN BOOT: Aborting boot due to Access Analytics environment prep failure. AA Response: {}".format(AAresponse))
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
                Logger.log("MAIN BOOT: Access Analytics Recovery Mode was activated.")
                AccessAnalytics.analyticsRecoveryMode()
            elif recoveryModeActionTwo == "no":
                print("MAIN: Recovery mode was not enabled. Access Boot is aborted.")
                Logger.log("MAIN BOOT: Aborting boot due to Access Analytics environment prep failure. AA Response: {}".format(AAresponse))
                sys.exit(1)
            else:
                print("MAIN: Invalid action provided. Access Boot is aborted.")
                sys.exit(1)
        else:
            print(AAresponse)
    else:
        print("MAIN: AccessAnalytics is not enabled and will not be setup and run.")

    # Port check
    portIsValid = True
    if 'RuntimePort' not in os.environ:
        print("MAIN: RuntimePort environment variable is not set in .env file. Access cannot be booted without a valid port set. Please re-boot Access after setting RuntimePort.")
        portIsValid = False
    elif not os.environ['RuntimePort'].isdigit():
        print("MAIN: RuntimePort environment variable has an invalid value. Port value must be an integer.")
        portIsValid = False
    
    if not portIsValid:
        Logger.log("MAIN BOOT: Aborting due to invalid/missing RuntimePort .env variable.")
        sys.exit(1)
    

    # Register all external routes

    ## Identity Meta Services
    from identityMeta import identityMetaBP
    app.register_blueprint(identityMetaBP)

    ## API
    from api import apiBP
    app.register_blueprint(apiBP)

    ## Email OTP Service
    from emailOTP import emailOTPBP
    app.register_blueprint(emailOTPBP)

    ## Portal Service
    from portal import portalBP
    app.register_blueprint(portalBP)

    ## Assets
    from assets import assetsBP
    app.register_blueprint(assetsBP)
        
    print("All services are online; boot pre-processing and setup completed.")
    print()
    print("Booting Access...")
    print()

    Logger.log("MAIN BOOT: System successfully booted.")
    app.run(host='0.0.0.0', debug=False, port=int(os.environ['RuntimePort']))

if __name__ == "__main__":
  bootFunction()