from bootCheck import BootCheck
BootCheck.check()

import os, sys, pprint
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from flask_limiter import Limiter
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

def getIP():
    return request.headers.get('X-Real-Ip', request.remote_addr)

### APP CONFIG
configManager = Config()

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Chute')
readableFileExtensions = ', '.join(["."+x for x in configManager.config["fileExtensions"]])

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, origins="*", supports_credentials=True, allow_private_network=True)
limiter = Limiter(
    getIP,
    app=app,
    default_limits=["100 per minute"],
    storage_uri="memory://",
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = configManager.getAllowedRequestSize() * 1000 * 1000
app.secret_key = os.environ['APP_SECRET_KEY']

def allowed_file(filename):
    return ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in configManager.config["fileExtensions"])

availableAssets = []
if os.path.isdir(os.path.join(os.getcwd(), "assets")):
    for file in os.listdir(os.path.join(os.getcwd(), "assets")):
        if os.path.isfile(os.path.join(os.getcwd(), "assets", file)):
            availableAssets.append(file)

# Interval cleaning agent
def cleaner():
    try:
        users = Identity.load()
        if users == None:
            return
        if not isinstance(users, list):
            Logger.log("MAIN CLEANER ERROR: Users not loaded as list.")
            return
        
        for user in users:
            if (Universal.utcNow() - Universal.fromUTC(user.created)).total_seconds() > 10800 and user.emailVerification.verified != True:
                user.getAuditLogs()
                if len(user.auditLogs.values()) > 0:
                    for logID in list(user.auditLogs.keys()):
                        user.deleteAuditLog(logID)
                
                user.getFiles()
                if len(user.files.values()) > 0:
                    for fileID in list(user.files.keys()):
                        user.deleteFile(fileID)
                
                if AFManager.checkIfFolderIsRegistered(user.id):
                    AFManager.deleteFolder(user.id)
                
                user.destroy()
                
                Logger.log("MAIN CLEANER: Unverified user '{}' (Created: {}) cleared.".format(user.email, user.created))
    except Exception as e:
        Logger.log("MAIN CLEANER ERROR: {}".format(e))

## Other pre-requisites
@app.before_request
def updateAnalytics():
    if configManager.getSystemLock() == True and request.path != "/":
        return "ERROR: Service Unavailable", 503
    
    if AccessAnalytics.permissionCheck() and not (request.path.startswith("/assets") or request.path.startswith("/src/assets") or request.path.startswith("/favicon.ico") or request.path.startswith("/logo")):
        res = AccessAnalytics.newRequest(type=request.method.upper())
        if isinstance(res, str) and res.startswith("AAError:"):
            Logger.log(res)

@app.route('/version')
def version():
    return render_template('version.html', versionNum="Version information could not be obtained." if Universal.version == None else Universal.version)

@app.route('/ip')
def ip():
    return getIP()

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/assets") or request.path.startswith("/src/assets") or request.path.startswith("/favicon.ico") or request.path.startswith("/logo"):
        if request.path.startswith("/logo"):
            return send_from_directory(os.path.join(os.getcwd(), "assets", "logo", "svg"), "logo-color.svg")
        
        asset = request.path.split("/")[-1]
        if asset in availableAssets:
            return send_from_directory(os.path.join(os.getcwd(), "assets"), asset)
        return "ERROR: Asset not found.", 404
    try:
        return redirect(url_for('frontend.homepage'))
    except:
        return "ERROR: Page not found.", 404

@app.errorhandler(413)
def requestEntityTooLarge(e):
    return "ERROR: Request entity too large.", 413

@app.errorhandler(429)
def tooManyRequests(e):
    return "ERROR: Too many requests.", 429

@app.errorhandler(500)
def internalServerError(e):
    return "ERROR: Internal server error.", 500

@app.errorhandler(503)
def serviceUnavailable(e):
    return "ERROR: Service unavailable.", 503

def boot():
    Universal.initAsync()
    
    ver = Universal.getVersion()
    if ver == "Version File Not Found":
        print("MAIN LOAD ERROR: No system version file detected. Boot aborted.")
        sys.exit(1)
    
    if os.environ.get("CLEANER_DISABLED", "False") != "True":
        Universal.store["CleanerID"] = Universal.asyncProcessor.addJob(cleaner, trigger=Trigger('interval', seconds=10))
        print("MAIN: Cleaning agent started.")
    
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
        response = AccessAnalytics.setupEnvironment()
        print(response)
    
    # Set up AFManager
    res = AFManager.setup()
    if not res:
        raise Exception("MAIN LOAD ERROR: AFManager failed to set up.")
    
    # Set up Emailer
    Emailer.checkContext()
    
    # Blueprint registrations
    
    ## Frontend
    from frontend import frontendBP
    app.register_blueprint(frontendBP)
    
    ## Identity API
    from identity import identityBP
    app.register_blueprint(identityBP)
    
    ## Directory API
    from directory import directoryBP
    app.register_blueprint(directoryBP, url_prefix='/directory')
    
    ## UserProfile API
    from userProfile import userProfileBP
    app.register_blueprint(userProfileBP, url_prefix="/profile")
    
    ## Sharing API
    from sharing import sharingBP
    app.register_blueprint(sharingBP, url_prefix="/sharing")
    
    if len(sys.argv) > 1 and sys.argv[1] == "r":
        print(DI.save(None))
    
    print()
    print("MAIN: All services online. Booting Access 'v{}'...".format(Universal.version))
    port = os.environ.get('RuntimePort', 8000)
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    boot()