import os, re
from flask import Flask, request, render_template, Blueprint, send_file, send_from_directory, url_for, redirect
from main import jsonOnly, checkAPIKey, enforceSchema, Identity, Encryption, Universal, AuditLog, Logger, Emailer

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
    if not re.match("^[a-zA-Z0-9]{1,12}$", username):
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