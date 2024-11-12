import os, re
from flask import Flask, request, render_template, Blueprint, url_for, redirect, session
from models import Identity, Logger, Universal, AuditLog, EmailVerification
from services import Encryption, Universal
from emailer import Emailer
from decorators import *

apiBP = Blueprint('api', __name__)

def dispatchEmailVerification(destEmail: str, otpCode: str):
    text = """
    Welcome to the Access family! To finish signing up, please enter the following OTP code onto the website:
    
    OTP Code: {}
    
    Kind regards,
    The Access Team
    
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    {}
    """.format(otpCode, Universal.copyright)
    
    Universal.asyncProcessor.addJob(
        Emailer.sendEmail,
        destEmail=destEmail,
        subject="Verify Email | Access",
        altText=text,
        html=render_template(
            "emails/otpEmail.html",
            otpCode=otpCode,
            copyright=Universal.copyright
        )
    )

@apiBP.route("/identity/new", methods=["POST"])
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
        
        accountCreatedLog = AuditLog(
            accountID=account.id,
            event="IdentityCreate",
            text="Created identity with username '{}' and email '{}'.".format(account.username, account.email)
        )
        
        account.auditLogs[account.id] = accountCreatedLog
        account.save()
    except Exception as e:
        Logger.log("IDENTITY NEW ERROR: Failed to create and save new identity. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    # Dispatch OTP verification email
    dispatchEmailVerification(account.email, otpCode)
    
    return "SUCCESS: Identity created. Verify email via OTP code dispatched.", 200

@apiBP.route("/identity/login", methods=["POST"])
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
            return "UERROR: Username or email does not exist.", 404
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
    
    loginEvent = AuditLog(
        accountID=account.id,
        event="Login",
        text="Logged in from IP address '{}'.".format(request.remote_addr)
    )
    account.auditLogs[loginEvent.id] = loginEvent
    
    account.save()
    
    # Update user session
    session["username"] = account.username
    session["authToken"] = authToken
    session["sessionStart"] = account.lastLogin
    
    return "SUCCESS: Logged in successfully.", 200

@apiBP.route("/identity/verifyOTP", methods=["POST"])
@jsonOnly
@checkAPIKey
@enforceSchema(
    ("usernameOrEmail", str),
    ("otpCode", str)
)
def verifyOTP():
    # Preprocess data
    usernameOrEmail: str = request.json["usernameOrEmail"].strip()
    otpCode: str = request.json["otpCode"].strip()
    
    if len(usernameOrEmail) == 0 or len(otpCode) == 0:
        return "UERROR: Username/email and OTP code cannot be empty.", 400
    
    # Check if email is even valid
    if "@" in usernameOrEmail:
        if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", usernameOrEmail):
            return "UERROR: Email is not in the correct format.", 400
    
    # Check if account exists and verify OTP
    account = None
    try:
        account = Identity.load(username=usernameOrEmail, email=usernameOrEmail)
        if not isinstance(account, Identity):
            return "UERROR: Account not found.", 404
    except Exception as e:
        Logger.log("IDENTITY OTP VERIFY ERROR: Failed to find identity. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    verificationInfo = account.emailVerification
    if verificationInfo.verified and verificationInfo.otpCode != None:
        verificationInfo.otpCode = None
        verificationInfo.otpCode = None
        verificationInfo.save()
        
        session.clear()
        return "UERROR: Something went wrong. Please verify your email and login again.", 401
    if verificationInfo.verified:
        return "UERROR: Email already verified.", 400
    if verificationInfo.otpCode == None:
        return "UERROR: No OTP code to verify.", 400
    if verificationInfo.otpCode != otpCode:
        return "UERROR: Invalid OTP code.", 401
    
    verificationInfo.otpCode = None
    verificationInfo.dispatchTimestamp = None
    verificationInfo.verified = True
    verificationInfo.save()
    
    return "SUCCESS: Email verified successfully.", 200

@apiBP.route("/identity/resendEmailVerification", methods=["POST"])
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
    
    dispatchEmailVerification(user.email, otpCode)
    
    return "SUCCESS: Email verification OTP code dispatched.", 200