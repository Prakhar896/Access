import os, re
from flask import Blueprint, request, redirect, url_for, session, render_template
from models import Identity, File, AuditLog
from decorators import jsonOnly, checkAPIKey, emailVerified, checkSession
from services import Universal, Logger, Encryption
from emailDispatch import dispatchEmailVerification, dispatchPasswordUpdatedEmail
from AFManager import AFManager, AFMError

userProfileBP = Blueprint('profile', __name__)

@userProfileBP.route('', methods=['POST'])
@checkAPIKey
@checkSession(strict=True, provideIdentity=True)
def getProfile(user: Identity):
    try:
        user.getFiles()
    except Exception as e:
        Logger.log("USERPROFILE GET ERROR: Failed to get user's files; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
        
    profileData = {
        "username": user.username,
        "email": user.email,
        "emailVerified": user.emailVerification.verified,
        "lastLogin": user.lastLogin,
        "createdAt": user.created,
        "fileCount": len(user.files)
    }
    
    return profileData, 200

@userProfileBP.route('/auditLogs', methods=['POST'])
@checkAPIKey
@checkSession(strict=True, provideIdentity=True)
def getAuditLogs(user: Identity):
    try:
        user.getAuditLogs()
    except Exception as e:
        Logger.log("USERPROFILE GET ERROR: Failed to get user's audit logs; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
    
    auditLogs = {}
    for logID, log in user.auditLogs.items():
        auditLogs[logID] = {
            "timestamp": log.timestamp,
            "event": log.event,
            "text": log.text
        }
    
    return auditLogs, 200

@userProfileBP.route('/update', methods=["POST"])
@checkAPIKey
@jsonOnly
@checkSession(strict=True, provideIdentity=True)
def updateProfile(user: Identity):
    username: str = None
    email: str = None
    currentPassword: str = None
    newPassword: str = None
    
    if "username" in request.json:
        if not isinstance(request.json["username"], str):
            return "ERROR: Invalid request format.", 400
        if len(request.json["username"].strip()) < 1:
            return "UERROR: Username must be at least 1 character long.", 400
        
        username = request.json["username"].strip()
        if not re.match("^[a-zA-Z0-9]{1,12}$", username) or not username.isalnum():
            return "UERROR: Username must be alphanumeric with no spaces and no longer than 12 characters.", 400
        
        if username == user.username:
            username = None
    
    if "email" in request.json:
        if not isinstance(request.json["email"], str):
            return "ERROR: Invalid request format.", 400
        
        email = request.json["email"].strip()
        if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return "UERROR: Email is not in the correct format.", 400
        
        if email == user.email:
            email = None
    
    if "newPassword" in request.json:
        if not isinstance(request.json["newPassword"], str):
            return "ERROR: Invalid request format.", 400
        
        if "currentPassword" not in request.json:
            return "ERROR: Invalid request format.", 400
        if not isinstance(request.json["currentPassword"], str):
            return "ERROR: Invalid request format.", 400
        
        newPassword = request.json["newPassword"].strip()
        currentPassword = request.json["currentPassword"].strip()
        if len(newPassword) < 6:
            return "UERROR: Password must be at least 6 characters long.", 400
        if newPassword == currentPassword:
            return "UERROR: New password cannot be the same as the old password.", 400
        
        numbers = False
        uppercaseChars = False
        specialChars = False
        for char in newPassword:
            if numbers and uppercaseChars and specialChars:
                break
            if char.isnumeric():
                numbers = True
            elif char.isupper():
                uppercaseChars = True
            elif not char.isalnum():
                specialChars = True
        if not (numbers and uppercaseChars and specialChars):
            return "UERROR: Password must have at least 1 number, 1 uppercase letter, and 1 special character.", 400
        
        if not Encryption.verifySHA256(currentPassword, user.password):
            return "UERROR: Incorrect password.", 400
        if Encryption.verifySHA256(newPassword, user.password):
            return "UERROR: New password cannot be the same as the old password.", 400
    
    if username is None and email is None and newPassword is None:
        return "SUCCESS: Nothing to update.", 200
    
    if (username != None or newPassword != None) and not user.emailVerification.verified:
        return "UERROR: Email must be verified before updating username or password.", 400
    
    # Try to see if there's another account with the same username/email
    if username != None or email != None:
        try:
            existingAccount = Identity.load(username=username, email=email)
            if existingAccount != None:
                return "UERROR: Username or email already in use.", 400
        except Exception as e:
            Logger.log("USERPROFILE UPDATE ERROR: Failed to check for existing account; error: {}".format(e))
            return "ERROR: Failed to process request.", 500
    
    # Update details
    if username != None:
        user.username = username
    
    if email != None:
        if user.emailVerification.dispatchTimestamp != None and isinstance(user.emailVerification.dispatchTimestamp, str):
            if (Universal.utcNow() - Universal.fromUTC(user.emailVerification.dispatchTimestamp)).total_seconds() < 120:
                return "UERROR: Email address can only be changed every 2 minutes.", 400
        
        user.email = email
        user.emailVerification.verified = False
        user.emailVerification.otpCode = Universal.generateUniqueID(customLength=6)
        user.emailVerification.dispatchTimestamp = Universal.utcNowString()
        
        dispatchEmailVerification(user.username, user.email, user.emailVerification.otpCode, user.id)
        
        Logger.log("USERPROFILE UPDATE: Identity '{}' changed their email to '{}'. Email verification dispatched.".format(user.id, user.email))
    
    if newPassword != None:
        user.password = Encryption.encodeToSHA256(newPassword)
        Logger.log("USERPROFILE UPDATE: Identity '{}' changed their password.".format(user.id))
        
        dispatchPasswordUpdatedEmail(user.username, user.email)
    
    user.save()
    
    return "SUCCESS: Profile updated.", 200

@userProfileBP.route('/delete', methods=["POST"])
@checkAPIKey
@checkSession(strict=True, provideIdentity=True)
def deleteIdentity(user: Identity):
    # Systematically delete all user-related resources
    try:
        user.getFiles()
    except Exception as e:
        Logger.log("USERPROFILE DELETE ERROR: Failed to retrieve user's files; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
    
    for fileID in list(user.files.keys()):
        try:
            user.deleteFile(fileID)
        except Exception as e:
            Logger.log("USERPROFILE DELETE ERROR: Failed to delete file object '{}' for '{}' identity deletion; error: {}".format(fileID, user.id, e))
    
    try:
        user.getAuditLogs()
    except Exception as e:
        Logger.log("USERPROFILE DELETE ERROR: Failed to retrieve user's audit logs; error: {}".format(e))
        return "ERROR: Failed to process request.", 500
    
    for logID in list(user.auditLogs.keys()):
        try:
            user.deleteAuditLog(logID)
        except Exception as e:
            Logger.log("USERPROFILE DELETE ERROR: Failed to delete audit log '{}' for '{}' identity deletion; error: {}".format(logID, user.id, e))
    
    try:
        if AFManager.checkIfFolderIsRegistered(user.id):
            res = AFManager.deleteFolder(user.id)
            if res != True:
                raise Exception(res)
    except AFMError as e:
        Logger.log("USERPROFILE DELETE ERROR: Failed to delete directory for user '{}' in AFM; error: {}".format(user.id, e))
        return "ERROR: Failed to process request.", 500
    
    try:
        user.destroy()
    except Exception as e:
        Logger.log("USERPROFILE DELETE ERROR: Failed to delete identity '{}'; error: {}".format(user.id, e))
        return "ERROR: Failed to process request.", 500
    
    session.clear()
    
    Logger.log("USERPROFILE DELETE: Identity '{}' ({}) deleted.".format(user.id, user.username))
    
    return "SUCCESS: Identity deleted. Thank you for using Access.", 200