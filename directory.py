import os, copy
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
        fileSaveLog.save()
        
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

@directoryBP.route('/file/<filename>', methods=['GET'])
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def downloadFile(user: Identity, filename: str):
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    if filename not in AFManager.getFilenames(user.id):
        return "ERROR: File not found.", 404
    
    userFile = [user.files[fileID] for fileID in user.files if user.files[fileID].name == filename]
    if len(userFile) == 0:
        Logger.log("DIRECTORY DOWNLOAD: Updating user '{}' with unmatched existing file '{}'.".format(user.id, filename))
        userFile = File(user.id, filename)
        userFile.save()
    else:
        userFile = userFile[0]
    
    return send_file(AFManager.userFilePath(user.id, filename), as_attachment=True, last_modified=Universal.fromUTC(userFile.lastUpdate) if isinstance(userFile.lastUpdate, str) else None)

@directoryBP.route('/file/<filename>', methods=['DELETE'])
@checkAPIKey
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def deleteFile(user: Identity, filename: str):
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    if filename not in AFManager.getFilenames(user.id):
        return "ERROR: File not found.", 404
    
    try:
        res = AFManager.deleteFile(user.id, filename)
        if res != True:
            raise Exception(res)
    except Exception as e:
        Logger.log("DIRECTORY DELETE ERROR: Operation failed for user '{}'; error: {}".format(user.id, e))
        return "ERROR: Failed to process request.", 500
    
    userFile = [user.files[fileID] for fileID in user.files if user.files[fileID].name == filename]
    if len(userFile) == 1:
        userFile = userFile[0]
        userFile.destroy()
    
    log = AuditLog(user.id, "FileDelete", "File '{}' deleted.".format(filename))
    log.save()
    
    return "SUCCESS: File deleted.", 200

@directoryBP.route('/bulkDelete', methods=['DELETE'])
@checkAPIKey
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def bulkDelete(user: Identity):
    filenames = [x.strip() for x in request.args.getlist('filenames')]
    if len(filenames) == 0:
        return "ERROR: No filenames provided.", 400
    
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    directoryFiles = AFManager.getFilenames(user.id)
    fileDeletionUpdates = {}
    changes = False
    for filename in filenames:
        if filename not in directoryFiles:
            fileDeletionUpdates[filename] = "UERROR: File not found."
            continue
        
        try:
            res = AFManager.deleteFile(user.id, filename)
            if res != True:
                raise Exception(res)
        except Exception as e:
            Logger.log("DIRECTORY BULKDELETE ERROR: Failed to delete file '{}' for user '{}'; error: {}".format(filename, user.id, e))
            fileDeletionUpdates[filename] = "ERROR: Failed to process request."
            continue
        
        userFile = [user.files[fileID] for fileID in user.files if user.files[fileID].name == filename]
        if len(userFile) == 1:
            userFile = userFile[0]
            
            try:
                user.deleteFile(userFile.id)
                changes = True
            except Exception as e:
                Logger.log("DIRECTORY BULKDELETE ERROR: Failed to delete '{}' file object for user '{}'; error: {}".format(filename, user.id, e))
        
        log = AuditLog(user.id, "FileDelete", "File '{}' deleted.".format(filename))
        log.save()
        changes = True
        
        fileDeletionUpdates[filename] = "SUCCESS: File deleted."
        
    if changes:
        user.save()
        
    return fileDeletionUpdates, 200

@directoryBP.route('/file', methods=['POST'])
@checkAPIKey
@jsonOnly
@enforceSchema(
    ("filename", str)
)
def getFile():
    if len(request.json['filename'].strip()) == 0:
        return "ERROR: No filename provided.", 400
    
    return redirect(url_for('directory.downloadFile', filename=request.json['filename'].strip()))

@directoryBP.route('/file', methods=['DELETE'])
@checkAPIKey
@jsonOnly
@enforceSchema(
    ("filenames")
)
def deleteFilesAPI():
    if isinstance(request.json["filenames"], str) or (isinstance(request.json["filenames"], list) and len(request.json["filenames"]) == 1):
        filename = (request.json["filenames"] if isinstance(request.json["filenames"], str) else request.json["filenames"][0]).strip()
        if len(filename) == 0:
            return "ERROR: No filename provided.", 400
        
        return redirect(url_for('directory.deleteFile', filename=filename))
    elif isinstance(request.json["filenames"], list):
        for filename in request.json["filenames"]:
            if not isinstance(filename, str) or len(filename.strip()) == 0:
                return "ERROR: Invalid filename provided.", 400
        
        return redirect(url_for('directory.bulkDelete', filenames=[filename.strip() for filename in request.json["filenames"]]))
    else:
        return "ERROR: Invalid request.", 400

@directoryBP.route('/', methods=['GET'])
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def listFiles(user: Identity):
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    directoryFiles = AFManager.getFilenames(user.id)
    userFilenames = [userFile.name for userFile in user.files.values()]
    filesData = {id: file for id, file in user.files.items()}
    
    # Check for new files in directory
    for directoryFile in directoryFiles:
        if directoryFile not in userFilenames:
            Logger.log("DIRECTORY LIST: Updating user '{}' with unmatched existing file '{}'.".format(user.id, directoryFile))
            newFile = File(user.id, directoryFile)
            newFile.linkTo(user)
            newFile.save()
            
            filesData[newFile.id] = newFile
    
    # Check for removed files in directory
    for userFilename in userFilenames:
        if userFilename not in directoryFiles:
            Logger.log("DIRECTORY LIST: Removing unmatched user file '{}' from user '{}'.".format(userFilename, user.id))
            userFile = user.files[[fileID for fileID in user.files if user.files[fileID].name == userFilename][0]]
            userFile.destroy()
            
            del filesData[userFile.id]
    
    filesData = {id: file.represent() for id, file in filesData.items()}
    return filesData, 200