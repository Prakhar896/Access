import os
from flask import render_template, request
from services import Universal, Logger
from emailer import Emailer

def dispatchAccountWelcome(username: str, destEmail: str):
    text = """
    Dear {},
    
    Thank you for signing up with Access, a secure, efficient and intuitive cloud storage service for all of your storage needs.
    With high reliability and a large set of useful features, you can be rest assured as Access takes on the bulk of the tedious file management tasks.
    
    After you verify your email, you will get access to a variety of tools and features to get started.
    Login to the Access Portal to intuitively see, manage and update your files and account information.
    We are so excited to have you on board!
    
    Thank you for being a valued user of Access.
    
    {}
    """.format(username, Universal.copyright)
    
    Universal.asyncProcessor.addJob(
        Emailer.sendEmail,
        destEmail=destEmail,
        subject="Welcome to Access!",
        altText=text,
        html=render_template(
            "emails/welcome.html",
            username=username,
            copyright=Universal.copyright
        )
    )

def dispatchEmailVerification(username: str, destEmail: str, otpCode: str, accountID: str):
    verificationLink = "{}verifyEmail?id={}&code={}".format(os.environ.get("SYSTEM_URL", "http://localhost:8000/"), accountID, otpCode)
    
    text = """
    Dear {},
    
    To benefit from Access' myriad of wonderful features, email verification is needed.
    
    If already on the verification page, enter this verification code: {}
    
    For easy verification, click on this link: {}
    
    Thank you for being a valued user of Access.
    
    
    {}
    """.format(username, otpCode, verificationLink, Universal.copyright)
    
    Universal.asyncProcessor.addJob(
        Emailer.sendEmail,
        destEmail=destEmail,
        subject="Verify Email | Access",
        altText=text,
        html=render_template(
            "emails/otpEmail.html",
            username=username,
            otpCode=otpCode,
            verificationLink=verificationLink,
            copyright=Universal.copyright
        )
    )

def dispatchPasswordResetKey(username: str, destEmail: str, resetKey: str):
    text = """
    Dear {},
    
    You requested a password reset on the Access Portal. Please enter the reset key below to continue your password reset.
    Please note that the reset key will only be available for 15 minutes.
    
    Reset Key: {}
    If you did not request a password reset, please ignore this email.
    
    Thank you for being a valued user of Access.
    
    {}
    """.format(username, resetKey, Universal.copyright)
    
    Universal.asyncProcessor.addJob(
        Emailer.sendEmail,
        destEmail=destEmail,
        subject="Password Reset Key | Access",
        altText=text,
        html=render_template(
            "emails/passwordResetKey.html",
            username=username,
            resetKey=resetKey,
            copyright=Universal.copyright
        )
    )

def dispatchPasswordUpdatedEmail(username: str, destEmail: str):
    text = """
    Dear {},
    
    This is an alert to notify that you recently updated your Access Identity's password on the portal.
    If this was not you, please reset your password immediately.
    
    Thank you for being a valued user of Access.
    
    {}
    """.format(username, Universal.copyright)
    
    Universal.asyncProcessor.addJob(
        Emailer.sendEmail,
        destEmail=destEmail,
        subject="Password Updated | Access",
        altText=text,
        html=render_template(
            "emails/passwordUpdated.html",
            username=username,
            copyright=Universal.copyright
        )
    )