import os, re
from flask import Blueprint, request, redirect, url_for
from models import Identity, File, AuditLog
from decorators import jsonOnly, checkAPIKey, emailVerified, checkSession
from identity import dispatchEmailVerification
from services import Universal, Logger, Encryption

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

@userProfileBP.route('/update', methods=["POST"])
@checkAPIKey
@jsonOnly
@checkSession(strict=True, provideIdentity=True)
def updateProfile(user: Identity):
    username: str = None
    email: str = None
    password: str = None
    
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
    
    if "password" in request.json:
        if not isinstance(request.json["password"], str):
            return "ERROR: Invalid request format.", 400
        
        password = request.json["password"].strip()
        if len(password) < 6:
            return "UERROR: Password must be at least 6 characters long.", 400
        
        numbers = False
        uppercaseChars = False
        specialChars = False
        for char in password:
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
        
        if Encryption.verifySHA256(password, user.password):
            return "UERROR: New password cannot be the same as the old password.", 400
    
    if username is None and email is None and password is None:
        return "SUCCESS: Nothing to update.", 200
    
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
        user.email = email
        user.emailVerification.verified = False
        user.emailVerification.otpCode = Universal.generateUniqueID(customLength=6)
        user.emailVerification.dispatchTimestamp = Universal.utcNowString()
        
        dispatchEmailVerification(user.email, otpCode=user.emailVerification.otpCode)
        
        Logger.log("USERPROFILE UPDATE: Identity '{}' changed their email to '{}'. Email verification dispatched.".format(user.id, user.email))
    
    if password != None:
        user.password = Encryption.encodeToSHA256(password)
        Logger.log("USERPROFILE UPDATE: Identity '{}' changed their password.".format(user.id))
    
    user.save()
    
    return "SUCCESS: Profile updated.", 200