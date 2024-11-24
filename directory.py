import os, copy, re, time, datetime
from typing import Dict, List
from io import BytesIO
from flask import Blueprint, request, send_file, send_from_directory, redirect, url_for
from werkzeug.datastructures.file_storage import FileStorage
from main import allowed_file, secure_filename, configManager
from AFManager import AFManager, AFMError
from services import Logger, Universal, Trigger
from models import Identity, File, AuditLog, EmailVerification
from decorators import jsonOnly, checkAPIKey, checkSession, enforceSchema, emailVerified, debug

directoryBP = Blueprint('directory', __name__)

def processUserUpload(name: str, file: FileStorage, user: Identity, fileExists: bool) -> str:
    try:
        file.save(AFManager.userFilePath(user.id, name))
    except Exception as e:
        Logger.log("DIRECTORY PROCESSUSERUPLOAD ERROR: Failed to save file '{}' for user '{}'; error: {}".format(name, user.id, e))
        return "ERROR: Failed to process request."
    
    # Log the file save
    fileSaveLog = AuditLog(user.id, "FileUpload" if not fileExists else "FileOverwrite", "File '{}' uploaded.".format(name))
    fileSaveLog.save()
    
    # Update the database with the file's list. If file exists, update last modified, else create and save new file object
    fileFound = False
    for userFile in user.files.values():
        if userFile.name == name:
            userFile.lastUpdate = Universal.utcNowString()
            fileFound = True
            userFile.save()
            break
    
    if not fileFound:
        fileObject = File(user.id, name)
        fileObject.save()
    
    if not fileExists:
        return "SUCCESS: File saved."
    else:
        return "SUCCESS: File updated."

def processUserBulkUpload(files: Dict[str,  BytesIO], user: Identity, currentFiles: List[str]):
    pass
    # content = file.read()
    
    # with open(path, 'wb') as f:
    #     f.write(content)  # Save file to the user directory
    #     print()
    #     print("\tFile saved to", path)
    #     print()

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


@directoryBP.route('', methods=['GET'])
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def listFiles(user: Identity):
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    directoryFiles = AFManager.getFilenames(user.id)
    
    userFiles = []
    userFilenames = []
    try:
        userFiles = File.load(accountID=user.id)
        if userFiles == None:
            userFiles = []
        if not isinstance(userFiles, list):
            raise Exception("Unexpected load response type.")
        
        userFilenames = [file.name for file in userFiles]
        userFiles = {file.id: file for file in userFiles}
    except Exception as e:
        Logger.log("DIRECTORY LIST ERROR: Failed to retrieve files for user '{}'; error: {}".format(user.id, e))
        return "ERROR: Failed to process request.", 500
    
    # Check for new files in directory
    for directoryFile in directoryFiles:
        if directoryFile not in userFilenames:
            Logger.log("DIRECTORY LIST: Updating user '{}' with unmatched existing file '{}'.".format(user.id, directoryFile))
            newFile = File(user.id, directoryFile)
            newFile.save()
            
            userFiles[newFile.id] = newFile
    
    # Check for removed files in directory
    for userFilename in userFilenames:
        if userFilename not in directoryFiles:
            Logger.log("DIRECTORY LIST: Removing unmatched user file '{}' from user '{}'.".format(userFilename, user.id))
            targetFile = [file for file in userFiles.values() if file.name == userFilename][0]
            targetFile.destroy()
            
            del userFiles[targetFile.id]
    
    filesData = {id: file.represent() for id, file in userFiles.items()}
    return filesData, 200

@directoryBP.route('', methods=['POST'])
@checkAPIKey
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def uploadFile(user: Identity):
    # Check presence of file in request
    if 'file' not in request.files:
        return "ERROR: No file part.", 400
    
    # Check if file is selected
    files = request.files.getlist('file')
    if len(files) == 0:
        return "UERROR: No file selected.", 400
    if len(files) > 10 and os.environ.get("DEBUG_MODE", "False") != "True":
        return "UERROR: Please upload a maximum of 10 files at a time.", 400
    
    # Check directory registration
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    # Get directory information
    currentFiles = AFManager.getFilenames(user.id)
    directorySize = AFManager.getDirectorySize(user.id, exclude=[secure_filename(file.filename) for file in files])
    if directorySize > configManager.getAllowedDirectorySize():
        print("hello")
        return "UERROR: Maximum upload size limit exceeded.", 400
    smallUpload = request.content_length < 10485760
    
    # Get database file objects
    try:
        user.getFiles()
    except Exception as e:
        Logger.log("DIRECTORY UPLOAD ERROR: Failed to retrieve files for user '{}'; error: {}".format(user.id, e))
        return "ERROR: Failed to process request.", 500
    
    fileSaveUpdates = {}
    approvedFiles: Dict[str, BytesIO] = {}
    for file in files:
        secureName = secure_filename(file.filename)
        if not allowed_file(file.filename):
            fileSaveUpdates[file.filename] = "UERROR: File type not allowed."
            continue
        if secureName not in currentFiles and (len(currentFiles) + 1) > configManager.getMaxFileCount():
            fileSaveUpdates[file.filename] = "UERROR: Maximum file upload limit reached."
            continue
          
        fileSize = AFManager.getFileSize(file)
        if (directorySize + fileSize) > configManager.getAllowedDirectorySize():
            print(directorySize, fileSize, configManager.getAllowedDirectorySize())
            fileSaveUpdates[file.filename] = "UERROR: Maximum upload size limit exceeded."
            continue
        
        # Update current directory information
        if secureName not in currentFiles:
            currentFiles.append(secureName)
        directorySize += fileSize
        
        fileExists = os.path.isfile(AFManager.userFilePath(user.id, secureName))
        if smallUpload:
            fileSaveUpdates[file.filename] = processUserUpload(secureName, file, user, fileExists)
        else:
            print("Large upload detected.")
            approvedFiles[secureName] = BytesIO(file.stream.read())
            fileSaveUpdates[file.filename] = "SUCCESS: Large upload ignored."
    
    return fileSaveUpdates, 200

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

@directoryBP.route('/file/<filename>', methods=['GET'])
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def downloadFile(user: Identity, filename: str):
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    if filename not in AFManager.getFilenames(user.id):
        return "ERROR: File not found.", 404
    
    userFile = None
    try:
        userFile = File.load(accountID=user.id, filename=filename)
        if not isinstance(userFile, File):
            raise Exception("Unexpected load response type.")
    except Exception as e:
        Logger.log("DIRECTORY DOWNLOAD ERROR: Failed to retrieve file object '{}' for user '{}'; error: {}".format(filename, user.id, e))
        return "ERROR: Failed to process request.", 500
    
    if userFile == None:
        Logger.log("DIRECTORY DOWNLOAD: Updating user '{}' with unmatched existing file '{}'.".format(user.id, filename))
        userFile = File(user.id, filename)
        userFile.save()
    
    lastModified = None
    if isinstance(userFile.lastUpdate, str):
        lastModified = Universal.fromUTC(userFile.lastUpdate)
    
    return send_file(AFManager.userFilePath(user.id, filename), as_attachment=True, last_modified=lastModified)

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
    
    userFile = File.load(accountID=user.id, filename=filename)
    if userFile != None and isinstance(userFile, File):
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
        
        try:
            userFile = File.load(accountID=user.id, filename=filename)
            if userFile != None and isinstance(userFile, File):
                userFile.destroy()
        except Exception as e:
            Logger.log("DIRECTORY BULKDELETE ERROR: Failed to delete file object '{}' for user '{}'; error: {}".format(filename, user.id, e))
            fileDeletionUpdates[filename] = "ERROR: Failed to process request."
            continue
        
        log = AuditLog(user.id, "FileDelete", "File '{}' deleted.".format(filename))
        log.save()
        
        fileDeletionUpdates[filename] = "SUCCESS: File deleted."
    
    return fileDeletionUpdates, 200

@directoryBP.route("/renameFile", methods=["POST"])
@checkAPIKey
@jsonOnly
@enforceSchema(
    ("filename", str),
    ("newFilename", str)
)
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def renameFile(user: Identity):
    filename: str = request.json["filename"].strip()
    newFilename: str = request.json["newFilename"].strip()
    
    if len(newFilename) == 0:
        return "ERROR: No new filename provided.", 400
    elif newFilename == filename:
        return "UERROR: New filename is the same as the existing filename.", 400
    
    if not AFManager.checkIfFolderIsRegistered(user.id):
        return "UERROR: Please register your directory first.", 400
    
    existingFiles = AFManager.getFilenames(user.id)
    if filename not in existingFiles:
        return "UERROR: File not found.", 404
    
    if newFilename in existingFiles:
        return "UERROR: New filename already exists.", 400
    
    # Check filename validity with re
    if not re.match(r"^[a-zA-Z0-9_\- ]+\.[a-zA-Z]+$", newFilename):
        return "UERROR: Invalid filename format.", 400
    
    newFilename = secure_filename(newFilename)
    
    try:
        res = AFManager.renameFile(user.id, filename, newFilename)
        if res != True:
            raise Exception(res)
    except Exception as e:
        Logger.log("DIRECTORY RENAMEFILE ERROR: Failed to rename file '{}' for user '{}'; error: {}".format(filename, user.id, e))
        return "ERROR: Failed to process request.", 500
    
    try:
        userFile = File.load(accountID=user.id, filename=filename)
        if userFile != None:
            userFile.name = newFilename
            userFile.lastUpdate = Universal.utcNowString()
            userFile.save()
        else:
            Logger.log("DIRECTORY RENAMEFILE WARNING: File object not found for existing file '{}' for user '{}'; creating new file object with new filename '{}'.".format(filename, user.id, newFilename))
            userFile = File(user.id, newFilename)
            userFile.lastUpdate = Universal.utcNowString()
            userFile.save()
    except Exception as e:
        Logger.log("DIRECTORY RENAMEFILE ERROR: Failed to update file object '{}' for user '{}'; error: {}".format(filename, user.id, e))
        return "ERROR: Failed to process request.", 500
    
    try:
        log = AuditLog(user.id, "FileRename", "File '{}' renamed to '{}'.".format(filename, newFilename))
        log.save()
    except Exception as e:
        Logger.log("DIRECTORY RENAMEFILE ERROR: Failed to log file rename operation for user '{}'; error: {}".format(user.id, e))
        return "ERROR: Failed to process request.", 500
    
    return "SUCCESS: File renamed.", 200