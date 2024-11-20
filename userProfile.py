from flask import Blueprint, request, redirect, url_for
from models import Identity, File, AuditLog
from decorators import jsonOnly, checkAPIKey, emailVerified, checkSession
from services import Universal, Logger

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
    return user.represent()