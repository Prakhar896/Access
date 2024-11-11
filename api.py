import os, re
from flask import Flask, request, render_template, Blueprint, url_for, redirect, session
from models import Identity, Logger, Universal, AuditLog
from services import Encryption
from emailer import Emailer
from decorators import *

apiBP = Blueprint('api', __name__)

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
            authToken=None,
            auditLogs={},
            otpCode=otpCode,
            created=Universal.utcNowString(),
            files={}
        )
        
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
    text = """
    Welcome to the Access family! To finish signing up, please enter the following OTP code onto the website:
    
    OTP Code: {}
    
    Kind regards,
    The Access Team
    
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    {}
    """.format(otpCode, Universal.copyright)
    
    Emailer.sendEmail(
        destEmail=account.email,
        subject="Verify Email | Access",
        altText=text,
        html=render_template(
            "emails/otpEmail.html",
            otpCode=otpCode,
            copyright=Universal.copyright
        )
    )
    
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
            return "UERROR: Invalid credentials.", 400
    except Exception as e:
        Logger.log("IDENTITY LOGIN ERROR: Failed to find identity. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    if not account.emailVerified:
        return "UERROR: Email not verified. Please verify your email first.", 400
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
            return "UERROR: Invalid credentials.", 401
    except Exception as e:
        Logger.log("IDENTITY OTP VERIFY ERROR: Failed to find identity. Error: {}".format(e))
        return "ERROR: Failed to process request. Please try again.", 500
    
    if account.emailVerified and account.otpCode != None:
        account.emailVerified = None
        account.otpCode = None
        account.save()
        
        session.clear()
        return "UERROR: Something went wrong. Please verify your email and login again.", 401
    if account.emailVerified:
        return "UERROR: Email already verified.", 400
    if account.otpCode == None:
        return "UERROR: No OTP code to verify.", 400
    if account.otpCode != otpCode:
        return "UERROR: Invalid OTP code.", 401
    
    account.otpCode = None
    account.emailVerified = True
    account.save()
    
    return "SUCCESS: Email verified successfully.", 200