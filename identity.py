import os, re
from flask import Flask, request, render_template, Blueprint, url_for, redirect, session
from models import Identity, Logger, Universal, AuditLog, EmailVerification
from services import Encryption, Universal
from accessAnalytics import AccessAnalytics
from AFManager import AFManager, AFMError
from main import limiter, getIP
from emailDispatch import dispatchAccountWelcome, dispatchEmailVerification, dispatchPasswordResetKey, dispatchPasswordUpdatedEmail
from decorators import *

identityBP = Blueprint('api', __name__)

@identityBP.route("/identity/new", methods=["POST"])
@limiter.limit("1 per 2 seconds")
@limiter.limit("5 per hour")
@jsonOnly
@checkAPIKey
@enforceSchema(
    ("username", str),
    ("email", str),
    ("password", str)
)
def newIdentity():
    # Preprocess data
    username: str = request.json["username"].strip()
    email: str = request.json["email"].strip()
    password: str = request.json["password"].strip()
    
    # Validate data
    if not re.match("^[a-zA-Z0-9]{1,12}$", username) or not username.isalnum():
        return "UERROR: Username must be alphanumeric with no spaces and no longer than 12 characters.", 400
    if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return "UERROR: Email is not in the correct format.", 400
    if len(password) < 6:
        return "UERROR: Password must have at least 6 characters.", 400
    
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
    
    # Check if account is already existing
    try:
        existing = Identity.load(username=username, email=email)
        if isinstance(existing, Identity):
            return "UERROR: Username or email already exists.", 400
    except Exception as e:
        Logger.log("IDENTITY NEW ERROR: Failed to check username and email existence. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    # Process new account
    otpCode = Universal.generateUniqueID(customLength=6)
    
    account = None
    try:
        account = Identity(
            username=request.json["username"],
            email=request.json["email"],
            password=Encryption.encodeToSHA256(request.json["password"]),
            lastLogin=None,
            authToken=None
        )
        account.emailVerification.otpCode = otpCode
        account.emailVerification.dispatchTimestamp = Universal.utcNowString()
        account.save()
        
        accountCreatedLog = AuditLog(
            accountID=account.id,
            event="IdentityCreate",
            text="Created identity with username '{}' and email '{}'.".format(account.username, account.email)
        )
        accountCreatedLog.save()
    except Exception as e:
        Logger.log("IDENTITY NEW ERROR: Failed to create and save new identity. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    # Dispatch welcome email
    dispatchAccountWelcome(account.username, account.email)
    
    # Dispatch OTP verification email
    dispatchEmailVerification(account.username, account.email, otpCode, account.id)
    
    res = AccessAnalytics.newIdentityCreation()
    if isinstance(res, str):
        Logger.log(res)
    
    res = AccessAnalytics.newEmailSent(count=2)
    if isinstance(res, str):
        Logger.log(res)
    
    return {
        "message": "SUCCESS: Identity created. Verify email via OTP code dispatched.",
        "aID": account.id
    }, 200

@identityBP.route("/identity/login", methods=["POST"])
@limiter.limit("5 per minute")
@jsonOnly
@checkAPIKey
@enforceSchema(
    ("usernameOrEmail", str),
    ("password", str)
)
@checkSession(provideIdentity=True)
def loginIdentity(user: Identity | None=None):
    if isinstance(user, Identity):
        return "SUCCESS: Already logged in to '{}'. Log out first.".format(user.username), 200
    
    # Preprocess data
    usernameOrEmail: str = request.json["usernameOrEmail"].strip()
    password: str = request.json["password"].strip()
    
    if len(usernameOrEmail) == 0 or len(password) == 0:
        return "UERROR: Username or password cannot be empty.", 400
    
    # Check if email is even valid
    if "@" in usernameOrEmail:
        if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", usernameOrEmail):
            return "UERROR: Email is not in the correct format.", 400
    
    # Check if account exists and verify password
    account = None
    try:
        account = Identity.load(username=usernameOrEmail, email=usernameOrEmail)
        if not isinstance(account, Identity):
            return "UERROR: Invalid credentials.", 400
    except Exception as e:
        Logger.log("IDENTITY LOGIN ERROR: Failed to find identity. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    # if not account.emailVerification.verified:
    #     return "UERROR: Email not verified. Please verify your email first.", 400
    if not Encryption.verifySHA256(password, account.password):
        return "UERROR: Invalid credentials.", 400
    
    # Generate auth token
    authToken = Universal.generateUniqueID(customLength=12)
    account.authToken = authToken
    account.lastLogin = Universal.utcNowString()
    account.save()
    
    loginEvent = AuditLog(
        accountID=account.id,
        event="Login",
        text="Logged in from IP address '{}'.".format(getIP())
    )
    loginEvent.save()
    
    # Update user session
    session["aID"] = account.id
    session["username"] = account.username
    session["authToken"] = authToken
    session["sessionStart"] = account.lastLogin
    
    res = AccessAnalytics.newSignin()
    if isinstance(res, str):
        Logger.log(res)
    
    return "SUCCESS: Logged in successfully.", 200

@identityBP.route("/identity/logout", methods=["GET"])
@checkSession(strict=True, provideIdentity=True)
def logout(user: Identity):
    user.authToken = None
    user.save()
    
    session.clear()
    
    res = AccessAnalytics.newSignout()
    if isinstance(res, str):
        Logger.log(res)
    
    return "SUCCESS: Logged out successfully.", 200

@identityBP.route("/identity/session", methods=["GET"])
@checkSession(strict=True)
def getSession():
    return {
        "message": "SUCCESS: Session parameters retrieved.",
        "session": {
            "aID": session["aID"],
            "username": session["username"],
            "sessionStart": session["sessionStart"]
        }
    }

@identityBP.route("/identity/verifyOTP", methods=["POST"])
@limiter.limit("5 per minute")
@jsonOnly
@checkAPIKey
@enforceSchema(
    ("otpCode", str)
)
def verifyOTP():
    # Preprocess data
    if "userID" not in request.json and "usernameOrEmail" not in request.json:
        return "ERROR: Invalid request.", 400
    
    userID: str = request.json["userID"].strip() if "userID" in request.json else None
    usernameOrEmail: str = request.json["usernameOrEmail"].strip() if "usernameOrEmail" in request.json else None
    otpCode: str = request.json["otpCode"].strip()
    
    if (userID == None and usernameOrEmail == None) or len(otpCode) == 0:
        return "ERROR: Invalid request.", 400
    
    # Check if email is even valid
    if usernameOrEmail != None and "@" in usernameOrEmail:
        if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", usernameOrEmail):
            return "UERROR: Email is not in the correct format.", 400
    
    # Check if account exists and verify OTP
    account = None
    try:
        account = Identity.load(id=userID, username=usernameOrEmail, email=usernameOrEmail)
        if not isinstance(account, Identity):
            return "UERROR: Account not found.", 404
    except Exception as e:
        Logger.log("IDENTITY VERIFYOTP ERROR: Failed to find identity. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    if account.emailVerification.verified and account.emailVerification.otpCode != None:
        account.emailVerification.otpCode = None
        account.emailVerification.otpCode = None
        account.emailVerification.save()
        
        session.clear()
        return "UERROR: Something went wrong. Please verify your email and login again.", 401
    if account.emailVerification.verified:
        return "UERROR: Email already verified.", 400
    if account.emailVerification.otpCode == None:
        return "UERROR: No code to verify.", 400
    if account.emailVerification.otpCode != otpCode:
        return "UERROR: Invalid verification code.", 401
    
    account.emailVerification.otpCode = None
    account.emailVerification.dispatchTimestamp = None
    account.emailVerification.verified = True
    account.save()
    
    emailVerifiedLog = AuditLog(
        accountID=account.id,
        event="EmailVerified",
        text="Email '{}' verified successfully.".format(account.email)
    )
    emailVerifiedLog.save()
    
    if not AFManager.checkIfFolderIsRegistered(account.id):
        res = AFManager.registerFolder(account.id)
        if isinstance(res, AFMError):
            Logger.log("IDENTITY VERIFYOTP ERROR: Failed to register folder for account '{}'. Error: {}".format(account.id, res))
        else:
            folderRegisteredLog = AuditLog(account.id, "DirectoryRegistered", "Registered storage directory for account.")
            folderRegisteredLog.save()
    
    return "SUCCESS: Email verified successfully.", 200

@identityBP.route("/identity/resendEmailVerification", methods=["POST"])
@limiter.limit("1 per 2 seconds")
@checkAPIKey
@checkSession(provideIdentity=True)
def resendEmailVerification(user: Identity | None=None):
    if not isinstance(user, Identity):
        if not request.is_json or "usernameOrEmail" not in request.json:
            return "ERROR: Invalid request.", 400
        
        # Since the user is not logged in, retrieve account manually
        
        ## Check if email is even valid
        usernameOrEmail = request.json["usernameOrEmail"].strip()
        if len(usernameOrEmail) == 0:
            return "UERROR: Username/email cannot be empty.", 400
        if "@" in usernameOrEmail:
            if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", usernameOrEmail):
                return "UERROR: Email is not in the correct format.", 400
        
        ## Check if account exists
        try:
            user = Identity.load(username=usernameOrEmail, email=usernameOrEmail)
            if not isinstance(user, Identity):
                return "UERROR: Account not found.", 404
        except Exception as e:
            Logger.log("IDENTITY RESEND EMAIL ERROR: Failed to find identity. Error: {}".format(e))
            return "ERROR: Failed to process request. Please try again.", 500
        
    if user.emailVerification.verified:
        return "UERROR: Email already verified.", 400
    if isinstance(user.emailVerification.dispatchTimestamp, str):
        if (Universal.utcNow() - Universal.fromUTC(user.emailVerification.dispatchTimestamp)).total_seconds() < 60:
            return "UERROR: Cannot resend verification email within 60 seconds of dispatch.", 400
    
    # Generate new OTP code and dispatch email
    otpCode = Universal.generateUniqueID(customLength=6)
    
    user.emailVerification.otpCode = otpCode
    user.emailVerification.dispatchTimestamp = Universal.utcNowString()
    user.emailVerification.save()
    
    dispatchEmailVerification(user.username, user.email, otpCode, user.id)
    
    res = AccessAnalytics.newEmailSent()
    if isinstance(res, str):
        Logger.log(res)
    
    return "SUCCESS: Email verification OTP code dispatched.", 200

@identityBP.route("/identity/forgotPassword", methods=["POST"])
@limiter.limit("2 per minute")
@checkAPIKey
@jsonOnly
@enforceSchema(
    ("usernameOrEmail", str)
)
def forgotPassword():
    usernameOrEmail = request.json["usernameOrEmail"].strip()
    
    ambiguousSuccessMessage = "SUCCESS: If an account exists with the provided username/email, a password reset key has been dispatched."
    
    if "@" in usernameOrEmail:
        if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", usernameOrEmail):
            return "UERROR: Email is not in the correct format.", 400
    
    account = None
    try:
        account = Identity.load(username=usernameOrEmail, email=usernameOrEmail)
        if not isinstance(account, Identity):
            return ambiguousSuccessMessage, 200
    except Exception as e:
        Logger.log("IDENTITY FORGOT PASSWORD ERROR: Failed to find identity. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    if "reset" not in request.json:
        if account.resetDispatch != None and isinstance(account.resetDispatch, str):
            if (Universal.utcNow() - Universal.fromUTC(account.resetDispatch)).total_seconds() < 60:
                return ambiguousSuccessMessage, 200
            
            if account.resetKey == None:
                account.resetDispatch = None
        
        resetKey = Universal.generateUniqueID(customLength=8)
        
        account.resetKey = resetKey
        account.resetDispatch = Universal.utcNowString()
        account.save()
        
        Logger.log("IDENTITY FORGOTPASSWORD: Password reset key dispatched for account '{}'.".format(account.id))
        
        dispatchPasswordResetKey(account.username, account.email, resetKey)
        
        res = AccessAnalytics.newEmailSent()
        if isinstance(res, str):
            Logger.log(res)
        
        return "SUCCESS: If an account exists with the provided username/email, a password reset email has been dispatched.", 200
    else:
        if not isinstance(request.json["reset"], dict):
            return "ERROR: Invalid request.", 400
        
        reqParams = ["key", "newPassword"]
        for param in reqParams:
            if param not in request.json["reset"]:
                return "ERROR: Invalid request.", 400
            elif not isinstance(request.json["reset"][param], str):
                return "ERROR: Invalid request.", 400
            elif len(request.json["reset"][param].strip()) == 0:
                return "UERROR: Invalid request.", 400
        
        resetKey: str = request.json["reset"]["key"].strip()
        newPassword: str = request.json["reset"]["newPassword"].strip()
        
        if len(newPassword) < 6:
            return "UERROR: Password must have at least 6 characters.", 400
        
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
        
        if account.resetKey == None or account.resetDispatch == None:
            return "UERROR: No reset key dispatched for account.", 400
        if (Universal.utcNow() - Universal.fromUTC(account.resetDispatch)).total_seconds() > 900:
            account.resetKey = None
            account.resetDispatch = None
            account.save()
            
            Logger.log("IDENTITY FORGOTPASSWORD: Password reset key expired for account '{}'.".format(account.id))
            
            return "UERROR: Reset key expired. Please request a new one.", 400
        
        if account.resetKey != resetKey:
            return "UERROR: Invalid reset key.", 401
        
        # Reset password
        account.authToken = None
        account.password = Encryption.encodeToSHA256(newPassword)
        account.resetKey = None
        account.resetDispatch = None
        account.save()
        
        dispatchPasswordUpdatedEmail(account.username, account.email)
        
        res = AccessAnalytics.newEmailSent()
        if isinstance(res, str):
            Logger.log(res)
        
        return "SUCCESS: Password updated successfully.", 200