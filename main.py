from bootCheck import BootCheck
BootCheck.check()

import os, sys
from flask import Flask, request, render_template
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
    else:
        print("DI: Setup complete.")
            
    # Set up Analytics
    if AccessAnalytics.permissionCheck():
        response = AccessAnalytics.prepEnvironmentForAnalytics()
        print(response)
        
    # Set up Emailer
    Emailer.checkContext()
    
    print()
    print("MAIN: All services online. Booting Access 'v{}'...".format(Universal.version))
    port = os.environ.get('RuntimePort', 8000)
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    boot()