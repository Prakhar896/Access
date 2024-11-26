import os
from flask import Flask, request, Blueprint, jsonify, redirect, url_for, send_file, send_from_directory
from main import limiter
from models import Identity, File, FileSharing
from AFManager import AFManager, AFMError
from services import Logger, Universal, Encryption
from decorators import checkAPIKey, jsonOnly, checkSession, emailVerified, enforceSchema

sharingBP = Blueprint("sharing", __name__)

@sharingBP.route("/new", methods=["POST"])
@limiter.limit("12 per minute")
@checkAPIKey
@jsonOnly
@enforceSchema(
    ("fileID", str),
    ("password")
)
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def newSharing(user: Identity):
    fileID = request.json["fileID"].strip()
    password = None
    
    if len(fileID) == 0:
        return "ERROR: Invalid request.", 400
    if isinstance(request.json["password"], str):
        password = request.json["password"].strip()
        if len(password) < 6:
            return "UERROR: Password must be at least 6 characters.", 400
    
    targetFile = None
    try:
        targetFile = File.load(fileID)
        if not isinstance(targetFile, File):
            return "ERROR: File not found.", 404
        if targetFile.accountID != user.id:
            return "ERROR: File not found.", 404
    except Exception as e:
        Logger.log("SHARING NEW ERROR: Failed to load target file; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
    
    # Check if last sharing was within 1 minute
    if isinstance(targetFile.sharing.startTimestamp, str):
        if (Universal.utcNow() - Universal.fromUTC(targetFile.sharing.startTimestamp)).total_seconds() < 60:
            return "UERROR: Please wait 1 minute before sharing again.", 400

    # Create new sharing
    targetFile.sharing.linkCode = Universal.generateUniqueID()
    if password != None:
        targetFile.sharing.password = Encryption.encodeToSHA256(password)
    else:
        targetFile.sharing.password = None
    targetFile.sharing.accessors = 0
    targetFile.sharing.startTimestamp = Universal.utcNowString()
    targetFile.sharing.active = True
    targetFile.sharing.save()
    
    Logger.log("SHARING NEW: User '{}' shared file '{}' with code '{}'.".format(user.id, targetFile.name, targetFile.sharing.linkCode))
    
    return jsonify({
        "message": "SUCCESS: File sharing successful.",
        "linkCode": targetFile.sharing.linkCode
    })

@sharingBP.route("/revoke", methods=["POST"])
@limiter.limit("12 per minute")
@checkAPIKey
@jsonOnly
@enforceSchema(
    ("fileID", str)
)
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def revokeSharing(user: Identity):
    fileID = request.json["fileID"].strip()
    
    if len(fileID) == 0:
        return "ERROR: Invalid request.", 400
    
    targetFile = None
    try:
        targetFile = File.load(fileID)
        if not isinstance(targetFile, File):
            return "UERROR: File not found.", 404
        if targetFile.accountID != user.id:
            return "UERROR: File not found.", 404
    except Exception as e:
        Logger.log("SHARING REVOKE ERROR: Failed to load target file; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
    
    if targetFile.sharing.linkCode == None:
        return "UERROR: Sharing is not active.", 400
    
    targetFile.sharing.linkCode = None
    targetFile.sharing.password = None
    targetFile.sharing.accessors = None
    targetFile.sharing.startTimestamp = None
    targetFile.sharing.active = False
    targetFile.sharing.save()
    
    Logger.log("SHARING REVOKE: User '{}' revoked sharing of file '{}'.".format(user.id, targetFile.name))
    
    return "SUCCESS: Sharing revoked."

@sharingBP.route("/toggleActiveStatus", methods=["POST"])
@limiter.limit("12 per minute")
@checkAPIKey
@jsonOnly
@enforceSchema(
    ("fileID", str),
    ("newStatus", bool)
)
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def toggleActive(user: Identity):
    fileID = request.json["fileID"].strip()
    newStatus = request.json["newStatus"]
    
    if len(fileID) == 0:
        return "ERROR: Invalid request.", 400
    
    targetFile = None
    try:
        targetFile = File.load(fileID)
        if not isinstance(targetFile, File):
            return "UERROR: File not found.", 404
        if targetFile.accountID != user.id:
            return "UERROR: File not found.", 404
    except Exception as e:
        Logger.log("SHARING TOGGLEACTIVE ERROR: Failed to load target file; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
    
    if targetFile.sharing.linkCode == None:
        return "UERROR: Sharing has not been activated.", 400
    
    targetFile.sharing.active = newStatus
    targetFile.sharing.save()
    
    Logger.log("SHARING TOGGLEACTIVE: User '{}' toggled sharing of file '{}' to '{}'.".format(user.id, targetFile.name, newStatus))
    
    return "SUCCESS: Sharing active status toggled."

@sharingBP.route("/info", methods=["POST"])
@limiter.limit("20 per minute")
@checkAPIKey
@jsonOnly
@checkSession(provideIdentity=True)
def getSharingInfo(user: Identity | None=None):
    linkCode = None
    if "linkCode" in request.json:
        linkCode = request.json["linkCode"].strip()
        
        if len(linkCode) == 0:
            return "ERROR: Invalid request.", 400
    
    fileID = None
    if "fileID" in request.json:
        fileID = request.json["fileID"].strip()
        
        if len(fileID) == 0:
            return "ERROR: Invalid request.", 400
    
    if linkCode == None and fileID == None:
        return "ERROR: Invalid request.", 400
    
    targetFile = None
    isOwner = False
    try:
        targetFile = File.load(id=fileID, shareCode=linkCode)
        if not isinstance(targetFile, File):
            return "UERROR: File not found.", 404
        
        if isinstance(user, Identity):
            if targetFile.accountID == user.id:
                isOwner = True
        
        if not isOwner and targetFile.sharing.active == False:
            return "UERROR: File not found.", 404
    except Exception as e:
        Logger.log("SHARING INFO ERROR: Failed to load target file; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
    
    ownerUsername = None
    if isOwner:
        ownerUsername = user.username
    else:
        try:
            owner = Identity.load(targetFile.accountID)
            if not isinstance(owner, Identity):
                raise Exception("Invalid load response for owner.")
            
            ownerUsername = owner.username
        except Exception as e:
            Logger.log("SHARING INFO ERROR: Failed to load owner of target file; error: {}".format(e))
            return "ERROR: Failed to process request.", 500
    
    data = {
        "name": targetFile.name,
        "owner": ownerUsername,
        "linkCode": targetFile.sharing.linkCode,
        "passwordRequired": targetFile.sharing.password != None
    }
    if isOwner:
        data["accessors"] = targetFile.sharing.accessors if targetFile.sharing.accessors != None else 0
        data["active"] = targetFile.sharing.active
        data["startTimestamp"] = targetFile.sharing.startTimestamp
    
    return jsonify(data)

@sharingBP.route("/get/<string:linkCode>", methods=["GET"])
@limiter.limit("12 per minute")
@checkSession(provideIdentity=True)
def getSharedFile(user: Identity | None=None, linkCode: str=None):
    if linkCode == None or len(linkCode) == 0:
        return "ERROR: Invalid request.", 400
    
    targetFile = None
    isOwner = False
    try:
        targetFile = File.load(shareCode=linkCode)
        if not isinstance(targetFile, File):
            return "ERROR: File not found.", 404
        if isinstance(user, Identity):
            if targetFile.accountID == user.id:
                isOwner = True
        
        if not isOwner and targetFile.sharing.active == False:
            return "ERROR: File not found.", 404
    except Exception as e:
        Logger.log("SHARING GET ERROR: Failed to load target file; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
    
    if isinstance(targetFile.sharing.password, str) and not isOwner:
        if request.args.get("password", None) == None:
            return "ERROR: Password required.", 401
        if not Encryption.verifySHA256(request.args.get("password"), targetFile.sharing.password):
            return "ERROR: Invalid password.", 401
    
    if not AFManager.checkIfFolderIsRegistered(targetFile.accountID):
        Logger.log("SHARING GET ERROR: Directory for user '{}' not registered despite valid active sharing.".format(targetFile.accountID))
        return "ERROR: File not found.", 404
    
    if not os.path.isfile(AFManager.userFilePath(targetFile.accountID, targetFile.name)):
        Logger.log("SHARING GET ERROR: File '{}' by '{}' not found despite valid active sharing.".format(targetFile.name, targetFile.accountID))
        return "ERROR: File not found.", 404
    
    targetFile.sharing.accessors += 1
    targetFile.sharing.save()
    
    lastModified = None
    if isinstance(targetFile.lastUpdate, str):
        lastModified = Universal.fromUTC(targetFile.lastUpdate)
    
    return send_file(AFManager.userFilePath(targetFile.accountID, targetFile.name), as_attachment=True, last_modified=lastModified)