import os
from flask import Blueprint, request, send_file, send_from_directory, redirect, url_for
from main import allowed_file, secure_filename, configManager
from AFManager import AFManager, AFMError
from services import Logger, Universal
from models import Identity, File, AuditLog, EmailVerification
from decorators import jsonOnly, checkAPIKey, checkSession, enforceSchema, emailVerified, debug

directoryBP = Blueprint('directory', __name__)

@directoryBP.route('/register', methods=['POST'])
@checkAPIKey
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def registerDirectory(user: Identity):
    if AFManager.checkIfFolderIsRegistered(user.id):
        return "SUCCESS: Directory already registered.", 200
    
    try:
        res = AFManager.registerFolder(user.id)
        if res != True:
            raise Exception(res)
    except Exception as e:
        Logger.log("DIRECTORY REGISTER ERROR: Operation failed for user '{}'; error: {}".format(user.id, res))
        return "ERROR: Failed to process request.", 500
    
    return "SUCCESS: Directory registered.", 200

@directoryBP.route('/', methods=['POST'])
@checkAPIKey
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def uploadFile(user: Identity):
    if 'file' not in request.files:
        return "ERROR: No file part.", 400
    
    files = request.files.getlist('file')
    if len(files) == 0:
        return "ERROR: No file selected.", 400
    
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    currentFiles = AFManager.getFilenames(user.id)
    if len(currentFiles) >= configManager.getMaxFileCount():
        return "UERROR: Maximum file upload limit reached.", 400
    
    changes = False
    fileSaveUpdates = {}
    for file in files:
        secureName = secure_filename(file.filename)
        if not allowed_file(secureName):
            fileSaveUpdates[secureName] = "UERROR: File type not allowed."
            continue
        if (len(currentFiles) + 1) >= configManager.getMaxFileCount():
            fileSaveUpdates[secureName] = "UERROR: Maximum file upload limit reached."
            continue
        
        currentFiles.append(secureName)
        
        fileExists = os.path.isfile(AFManager.userFilePath(user.id, secureName))
        file.save(AFManager.userFilePath(user.id, secureName))
        fileSaveUpdates[secureName] = "SUCCESS: File saved."
        
        fileSaveLog = AuditLog(user.id, "FileUpload" if not fileExists else "FileOverwrite", "File '{}' uploaded.".format(secureName))
        fileSaveLog.linkTo(user)
        
        fileFound = False
        for userFile in user.files.values():
            if userFile.name == secureName:
                userFile.lastUpdate = Universal.utcNowString()
                fileFound = True
                break
        if not fileFound:
            fileObject = File(user.id, secureName)
            fileObject.linkTo(user)
        
        changes = True
    
    if changes:
        user.save()
    
    return fileSaveUpdates, 200