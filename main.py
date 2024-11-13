from bootCheck import BootCheck
BootCheck.check()

import os, sys
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
from services import *
from models import *
from config import Config
from activation import initActivation, makeKVR
from AFManager import AFManager, AFMError
from emailer import Emailer
from accessAnalytics import AccessAnalytics
from dotenv import load_dotenv
load_dotenv()

Universal.initAsync()

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

availableAssets = []
if os.path.isdir(os.path.join(os.getcwd(), "assets")):
    for file in os.listdir(os.path.join(os.getcwd(), "assets")):
        if os.path.isfile(os.path.join(os.getcwd(), "assets", file)):
            availableAssets.append(file)

print("MAIN BOOT: Assets available: " + ", ".join(availableAssets))

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

@app.route('/version')
def version():
    return render_template('version.html', versionNum="Version information could not be obtained." if Universal.version == None else Universal.version)

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/assets") or request.path.startswith("/src/assets") or request.path.startswith("/favicon.ico"):
        asset = request.path.split("/")[-1]
        if asset in availableAssets:
            return send_from_directory(os.path.join(os.getcwd(), "assets"), asset)
        return "ERROR: Asset not found.", 404
    return redirect(url_for('version'))

def boot():
    ver = Universal.getVersion()
    if ver == "Version File Not Found":
        print("MAIN LOAD ERROR: No system version file detected. Boot aborted.")
        sys.exit(1)
    
    # Set up FireConn
    if FireConn.checkPermissions():
        response = FireConn.connect()
        if response != True:
            print("MAIN LOAD WARNING: FireConn failed to connect. Error: {}".format(response))
    
    # Set up Database Interface
    response = DI.setup()
    if response != True:
        if isinstance(response, DIError):
            print("MAIN LOAD ERROR: DIError in DI setup: {}".format(response))
            sys.exit(1)
        else:
            print("MAIN LOAD ERROR: Unknown error in setting up DI: {}".format(response))
            sys.exit(1)
            
    # Set up Analytics
    if AccessAnalytics.permissionCheck():
        response = AccessAnalytics.prepEnvironmentForAnalytics()
        print(response)
        
    # Set up Emailer
    Emailer.checkContext()
    
    # Blueprint regirstrations
    
    ## API
    from api import apiBP
    app.register_blueprint(apiBP)
    
    if len(sys.argv) > 1 and sys.argv[1] == "r":
        print(DI.save(None))
    
    print()
    print("MAIN: All services online. Booting Access 'v{}'...".format(Universal.version))
    port = os.environ.get('RuntimePort', 8000)
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    boot()