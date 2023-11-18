from main import accessIdentities, validOTPCodes, fileUploadLimit, readableFileExtensions, CertAuthority, AFManager, AFMError, CAError, AccessAnalytics, Emailer, Encryption, Universal, Logger, obtainTargetIdentity, generateAuthToken
from flask import Flask, request, render_template, Blueprint, send_file, send_from_directory, url_for, redirect
import re, os, sys, json, random, copy, datetime, time

apiBP = Blueprint('api', __name__)

def headersCheck(headers):
    ## Headers check
    if 'Content-Type' not in headers:
        return "ERROR: Invalid headers."
    if 'AccessAPIKey' not in headers:
        return "ERROR: Invalid headers."

    if headers['Content-Type'] != 'application/json':
        return "ERROR: Content-Type header had incorrect value for this API request (expected application/json). Request failed."
    if headers['AccessAPIKey'] != os.environ['AccessAPIKey']:
        return "ERROR: Incorrect AccessAPIKey value for this API request. Request failed."

    return True

@apiBP.route('/api/createIdentity', methods=['POST'])
def makeAnIdentity():
    global validOTPCodes
    global accessIdentities
    if ('Content-Type' not in request.headers) or ('AccessAPIKey' not in request.headers):
        return "ERROR: One or more headers were not present in the API request. Request failed."
    
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    if 'username' not in request.json:
        return "ERROR: Invalid request body."
    if 'password' not in request.json:
        return "ERROR: Invalid request body."
    if 'email' not in request.json:
        return "ERROR: Invalid request body."
    if 'otpCode' not in request.json:
        return "ERROR: Invalid request body."

    # Checks for username validity
    if request.json['username'] in accessIdentities:
        return "UERROR: Username already taken."
    elif request.json['username'] == "":
        return "UERROR: Username cannot be blank."
    elif " " in request.json['username']:
        return "UERROR: Username cannot have spaces."
        
    # Check if email is already taken
    if request.json['email'] in [accessIdentities[x]['email'] for x in accessIdentities]:
        return "UERROR: Email already taken."

    # Check if otp code is valid
    if request.json['email'] not in validOTPCodes:
        Logger.log("API MAKEIDENTITY: OTP code could not be verified as email associated with code was not in database, likely due to a missing OTP email request.")
        return "ERROR: An error occurred. Please try again."
    if request.json['otpCode'] != validOTPCodes[request.json['email']]:
        return "UERROR: OTP code is incorrect."

    # Check if password is secure enough
    specialCharacters = list('!@#$%^&*()_-+')

    hasSpecialChar = False
    hasNumericDigit = False
    for char in request.json['password']:
        if char.isdigit():
            hasNumericDigit = True
        elif char in specialCharacters:
            hasSpecialChar = True

    if not (hasSpecialChar and hasNumericDigit):
        return "UERROR: Password must have at least 1 special character and 1 numeric digit."

    validOTPCodes.pop(request.json['email'])
    with open('validOTPCodes.txt', 'w') as f:
        json.dump(validOTPCodes, f)

    # Create new identity
    accessIdentities[request.json['username']] = {
        'password': Encryption.encodeToSHA256(request.json['password']),
        'email': request.json['email'],
        'otpCode': request.json['otpCode'],
        'sign-up-date': datetime.datetime.now().strftime(Universal.systemWideStringDateFormat),
        'last-login-date': datetime.datetime.now().strftime(Universal.systemWideStringDateFormat),
        'associatedCertID': CertAuthority.issueCertificate(request.json['username'])['certID'],
        'AF_and_files': {},
        'settings': {
            "emailPref": {
                "loginNotifs": True,
                "fileUploadNotifs": False,
                "fileDeletionNotifs": False
            }
        },
        'folderRegistered': False
    }

    # Save identities to file
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))
    CertAuthority.saveCertificatesToFile(fileObject=open('certificates.txt', 'w'))
    Logger.log("API MAKEIDENTITY: Successfully created identity with username '{}'.".format(request.json['username']))

    return "SUCCESS: Identity created."

@apiBP.route('/api/loginIdentity', methods=['POST'])
def loginIdentity():
    global accessIdentities
    CertAuthority.expireOldCertificates()
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))

    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    if 'email' not in request.json:
        return "ERROR: Invalid request body."
    if 'password' not in request.json:
        return "ERROR: Invalid request body."

    targetIdentity = obtainTargetIdentity(request.json['email'], accessIdentities)
    
    if targetIdentity == {}:
        return "UERROR: Invalid email or password."
    
    if not Encryption.verifySHA256(request.json['password'], targetIdentity["password"]):
        Logger.log("API LOGINIDENTITY: Blocked unauthorised login attempt for '{}'.".format(targetIdentity["username"]))
        return "UERROR: Invalid email or password."
    
    identityCertificate = CertAuthority.getCertificate(targetIdentity['associatedCertID'])
    if identityCertificate is None:
        return "UERROR: Could not find certificate associated with this identity. Authorisation failed."
    if identityCertificate['revoked'] == True:
        if identityCertificate['revocationReason'] == 'This certificate is expired.':
            return "UERROR: The certificate associated with this identity has expired. Authorisation failed."
        else:
            return "UERROR: The certificate associated with this identity has been revoked. Authorisation failed."
        
    if CAError.checkIfErrorMessage(CertAuthority.checkCertificateSecurity(identityCertificate)):
        return { "userMessage": "UERROR: The certificate associated with this identity has failed security checks. Authorisation failed.", "errorMessage": CertAuthority.checkCertificateSecurity(identityCertificate) }

    accessIdentities[targetIdentity['username']]['last-login-date'] = datetime.datetime.now().strftime(Universal.systemWideStringDateFormat)
    accessIdentities[targetIdentity['username']]['loggedInAuthToken'] = generateAuthToken()
    with open('accessIdentities.txt', 'w') as f:
        json.dump(accessIdentities, f)

    Logger.log("API LOGINIDENTITY: Identity '{}' signed in.".format(targetIdentity['username']))

    text = """
    Hi {},
    
    You have successfully logged in to the Access Identity System. If you do not recognise this login, please logout immediately at the link below or change the password.
    This login alert is automatically delivered to you by the Access System; if you wish not to receive these emails any further, please change your Access Identity email preferences in the Access Portal.

    Logout Link: {}

    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.

    Kind Regards,
    The Access Team
    """.format(
        targetIdentity['username'],
        "{}/identity/logout?authToken={}&username={}".format(request.host_url, accessIdentities[targetIdentity['username']]['loggedInAuthToken'], targetIdentity['username'])
        )

    html = render_template(
        "emails/loginEmail.html", 
        userName=targetIdentity['username'], 
        datetime=datetime.datetime.now().strftime(Universal.systemWideStringDateFormat) + ' UTC' + time.strftime('%z'), 
        logoutLink=("{}/identity/logout?authToken={}&username={}".format(request.host_url, accessIdentities[targetIdentity['username']]['loggedInAuthToken'], targetIdentity['username']))
        )

    ## SEND EMAIL
    if 'settings' in targetIdentity and 'emailPref' in targetIdentity['settings'] and targetIdentity['settings']['emailPref']['loginNotifs'] == True:
        Emailer.sendEmail(targetIdentity['email'], "Access Identity Login Alert", text, html)

    ## Update Access Analytics with sign in metric
    response = AccessAnalytics.newSignin()
    if isinstance(response, str):
        if response.startswith("AAError:"):
            print("API: Error in updating Analytics with new sign in; Response: {}".format(response))
        else:
            print("API: Unexpected response when attempting to update Analytics with new sign in; Response: {}".format(response))

    if 'GitpodEnvironment' in os.environ and os.environ['GitpodEnvironment'] == 'True':
        return "SUCCESS: Identity logged in. Auth Session Data: {}-{}".format(accessIdentities[targetIdentity['username']]['loggedInAuthToken'], targetIdentity['associatedCertID'])

    ## Update Access Analytics
    if 'settings' in targetIdentity and 'emailPref' in targetIdentity['settings'] and targetIdentity['settings']['emailPref']['loginNotifs'] == True:
        response = AccessAnalytics.newEmail(targetIdentity['email'], text, "Access Identity Login Alert", targetIdentity['username'])
        if isinstance(response, str):
            if response.startswith("AAError:"):
                print("API: There was an error in updating Analytics with new email data; Response: {}".format(response))
            else:
                print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))
        elif isinstance(response, bool) and response == True:
            print("API: Successfully updated Analytics with new email data.")
        else:
            print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))

    return "SUCCESS: Identity logged in. Auth Session Data: {}-{}".format(accessIdentities[targetIdentity['username']]['loggedInAuthToken'], targetIdentity['associatedCertID'])
    
@apiBP.route('/api/registerFolder', methods=['POST'])
def registerFolder():
    global accessIdentities

    ## Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Data body check
    if 'username' not in request.json:
        return "ERROR: Invalid request body."
    if request.json['username'] not in accessIdentities:
        return "ERROR: Username not associated with any Access Identity."
    
    ## Folder already exists check
    if AFManager.checkIfFolderIsRegistered(request.json['username']):
        return "ERROR: Folder for the Access Identity is already registered."
    
    ## Checks completed

    ## Register folder under username
    AFManager.registerFolder(request.json['username'])
    Logger.log("API REGISTERFOLDER: Registered folder for identity '{}'.".format(request.json['username']))

    ## Send email

    text = """
    Hi {},

    Congratulations on registering your Access Folder! You can now upload upto a maximum of {} files, each not bigger than 16MB in size that have the following allowed file extensions:
    {}

    Kind Regards,
    The Access Team

    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    Copyright 2022 Prakhar Trivedi
    """.format(request.json['username'], fileUploadLimit, readableFileExtensions)

    html = render_template('emails/folderRegistered.html', username=request.json['username'], fileUploadLimit=fileUploadLimit, fileExtensions=readableFileExtensions)

    ## Send email
    Emailer.sendEmail(accessIdentities[request.json['username']]['email'], "Access Folder Registered!", text, html)

    ## Update Access Identity
    accessIdentities[request.json['username']]['folderRegistered'] = True

    with open('accessIdentities.txt', 'w') as f:
        json.dump(accessIdentities, f)

    if 'AccessAnalyticsEnabled' in os.environ and os.environ['AccessAnalyticsEnabled'] == 'True':
        return "SUCCESS: Access Folder for {} registered!".format(request.json['username'])

    ## Update Access Analytics
    response = AccessAnalytics.newEmail(accessIdentities[request.json['username']]['email'], text, "Access Folder Registered!", request.json['username'])
    if isinstance(response, str):
        if response.startswith("AAError:"):
            print("API: There was an error in updating Analytics with new email data; Response: {}".format(response))
        else:
            print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))
    elif isinstance(response, bool) and response == True:
        print("API: Successfully updated Analytics with new email data.")
    else:
        print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))

    return "SUCCESS: Access Folder for {} registered!".format(request.json['username'])

@apiBP.route('/api/logoutIdentity', methods=['POST'])
def logoutIdentity():
    global accessIdentities

    # Headers Check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check
    
    # Body check
    if 'username' not in request.json:
        return "ERROR: Invalid request body."
    if 'authToken' not in request.json:
        return "ERROR: Invalid request body."
    if request.json['username'] not in accessIdentities:
        return "UERROR: Given username is not associated with any Access Identity."
    if 'loggedInAuthToken' not in accessIdentities[request.json['username']]:
        return "UERROR: Access Identity is not logged in. Only logged in identities can be logged out."
    if request.json['authToken'] != accessIdentities[request.json['username']]['loggedInAuthToken']:
        Logger.log("API LOGOUTIDENTITY: Blocked unauthorised logout attempt for '{}'.")
        return "UERROR: Invalid credentials provided for logout."
    
    # Logout process
    try:
        del accessIdentities[request.json['username']]['loggedInAuthToken']
        with open('accessIdentities.txt', 'w') as f:
            json.dump(accessIdentities, f)
        Logger.log("API LOGOUTIDENTITY: Identity '{}' logged out.".format(request.json['username']))

        ## Update Access Analytics
        response = AccessAnalytics.newSignout()
        if isinstance(response, str):
            if response.startswith("AAError:"):
                print("API: Error in updating Analytics with new sign out; Response: {}".format(response))
            else:
                print("API: Unexpected response when attempting to update Analytics with new sign out; Response: {}".format(response))

    except Exception as e:
        print("API: An error occurred in logging out an identity.")
        Logger.log("API LOGOUTIDENTITY ERROR: Error in logging out '{}': {}".format(request.json['username'], e))
        return "ERROR: An error occurred in logging out. Please try again."
    
    return "SUCCESS: Logged out user {}.".format(request.json['username'])

@apiBP.route('/api/deleteFile', methods=['POST'])
def deleteFileFromFolder():
    global accessIdentities

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'username' not in request.json:
        return "ERROR: Invalid request body."
    if request.json['username'] not in accessIdentities:
        return "UERROR: Username is not associated with any Access Identity. Please try again."
    if 'filename' not in request.json:
        return "ERROR: Invalid request body."

    if not AFManager.checkIfFolderIsRegistered(username=request.json['username']):
        return "UERROR: Folder for the Access Identity associated with that username has not been registered."
    
    files = AFManager.getFilenames(username=request.json['username'])

    if request.json['filename'] not in files:
        return "UERROR: No such file exists under your Access Folder."
    
    # Deletion of file

    response = AFManager.deleteFile(username=request.json['username'], filename=request.json['filename'])
    if AFMError.checkIfErrorMessage(response):
        Logger.log("API DELETEFILE ERROR: Failed to delete file from folder; AFM response: {}".format(response))
        return "ERROR: Failed to delete file. Please try again."
    elif response == "AFM: Successfully deleted the file.":
        ## Update Access Identity
        identityUsername = ''
        targetIdentity = {}
        for username in accessIdentities:
            if username == request.json['username']:
                targetIdentity = copy.deepcopy(accessIdentities[username])
                identityUsername = username

        if request.json['filename'] in targetIdentity["AF_and_files"]:
            targetIdentity["AF_and_files"].pop(request.json['filename'])
            accessIdentities[identityUsername]['AF_and_files'].pop(request.json['filename'])
        else:
            Logger.log("API DELETEFILE WARNING: When updating '{}' with file deletion, file name was not found in identity. System will continue regardless.".format(identityUsername))
            print("API: When updating Access Identity with file deletion, file's name was not found in the identity. Recovering and continuing...")

        with open('accessIdentities.txt', 'w') as f:
            json.dump(accessIdentities, f)

        Logger.log("API DELETEFILE: Deleted a file for '{}'.".format(identityUsername))

        ## Update Access Analytics
        response = AccessAnalytics.newFileDeletion()
        if isinstance(response, str):
            if response.startswith("AAError:"):
                print("API: Error in updating Analytics with new file deletion; Response: {}".format(response))
            else:
                print("API: Unexpected response when attempting to update Analytics with new file deletion; Response: {}".format(response))

        ## Send Email

        text = """
        Hi {},

        This email is a notification that you recently deleted a file with the name: '{}'.

        If this was you, please ignore this email. If it was not, please login to the Access Portal immediately and change your password.

        THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.</p>
        Copyright 2022 Prakhar Trivedi
        """.format(request.json['username'], request.json['filename'])

        html = render_template('emails/fileDeleted.html', username=request.json['username'], filename=request.json['filename'])

        ### Send the email itself
        if 'settings' in targetIdentity and 'emailPref' in targetIdentity['settings'] and targetIdentity['settings']['emailPref']['fileDeletionNotifs'] == True:
            Emailer.sendEmail(targetIdentity['email'], "File Deletion | Access Portal", text, html)

            ## Update Access Analytics
            response = AccessAnalytics.newEmail(accessIdentities[request.json['username']]['email'], text, "File Deletion | Access Portal", request.json['username'])
            if isinstance(response, str):
                if response.startswith("AAError:"):
                    print("API: There was an error in updating Analytics with new email data; Response: {}".format(response))
                else:
                    print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))
            elif isinstance(response, bool) and response == True:
                print("API: Successfully updated Analytics with new email data.")
            else:
                print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))

        return "SUCCESS: File {} belonging to user {} was successfully deleted.".format(request.json['filename'], request.json['username'])
    else:
        print("API: Unidentified response received from AFManager when executing delete file function. Response: {}".format(response))
        return "ERROR: Unknown response received from AFManager service. Check server logs for more information."

@apiBP.route('/api/userPreferences', methods=["POST"])
def fetchUserPreferences():
    global accessIdentities

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'certID' not in request.json:
        return "ERROR: Invalid request body."
    
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."
    
    if 'resourceReq' not in request.json:
        return "ERROR: Invalid request body."
    if request.json['resourceReq'] not in ['emailPrefs']:
        return "ERROR: Invalid resource was requested."

    # Response to request
    if request.json['resourceReq'] == 'emailPrefs':
        responseObject = copy.deepcopy(targetIdentity['settings']['emailPref'])
        responseObject['responseStatus'] = "SUCCESS"
        return responseObject

@apiBP.route('/api/updateUserPreference', methods=['POST'])
def updateUserPreference():
    global accessIdentities

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'certID' not in request.json:
        return "ERROR: Invalid request body."
    
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."
    
    if 'resourceReq' not in request.json:
        return "ERROR: Invalid request body."
    if request.json['resourceReq'] not in ['emailPrefs', 'certData', 'identityInfo']:
        return "ERROR: Invalid resource was requested."

    if 'preferenceName' not in request.json:
        return "ERROR: Invalid request body."

    if 'newValue' not in request.json:
        return "ERROR: Invalid request body."
    
    ## Update preference and respond
    if request.json['resourceReq'] == "emailPrefs":
        if request.json["preferenceName"] not in ['loginNotifs', 'fileUploadNotifs', 'fileDeletionNotifs']:
            return "ERROR: Given preference name for that settings resource does not exist."

        accessIdentities[targetIdentity['username']]['settings']['emailPref'][request.json['preferenceName']] = request.json['newValue']
        targetIdentity['settings']['emailPref'][request.json['preferenceName']] = request.json['newValue']

        with open('accessIdentities.txt', 'w') as f:
            json.dump(accessIdentities, f)

        responseObject = copy.deepcopy(targetIdentity['settings']['emailPref'])
        responseObject['responseStatus'] = "SUCCESS"
        Logger.log("API UPDATEUSERPREFERENCE: Updated preference for '{}'.".format(targetIdentity['username']))

        return responseObject
    else:
        # Temporary return before other settings resources are added
        return "ERROR: Other settings resources are not supported currently."

@apiBP.route('/api/confirmEmailUpdate', methods=['POST'])
def confirmEmailUpdate():
    global accessIdentities
    global validOTPCodes

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'newEmail' not in request.json:
        return "ERROR: Invalid request body."
    if 'currentPass' not in request.json:
        return "ERROR: Invalid request body."
    if 'certID' not in request.json:
        return "ERROR: Invalid request body."

    ## Get identity from certID
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."

    ## Check current password
    if not Encryption.verifySHA256(request.json['currentPass'], targetIdentity['password']):
        Logger.log("API CONFIRMEMAILUPDATE: Blocked unauthorised attempt to send OTP verification email for identity '{}'.".format(targetIdentity['username']))
        return "UERROR: Password is incorrect."

    ## Check if it is a valid email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", request.json['newEmail']):
        return "UERROR: That is not a valid email."

    for username in accessIdentities:
        if accessIdentities[username]['email'] == request.json['newEmail']:
            return "UERROR: That email is already taken."

    # Generate OTP Code
    numbers = [str(i) for i in range(10)]
    otp = ''.join(random.choice(numbers) for i in range(6))

    validOTPCodes[request.json['newEmail']] = otp
    with open('validOTPCodes.txt', 'w') as f:
        json.dump(validOTPCodes, f)

    # Send email
    text = """
    Hi {},

    You recently requested to update your Access Identity email on the Access Portal. Please enter the OTP code below to verify this email.

    OTP Code: {}

    Was not you? Please kindly ignore this email. Apologies for any inconveniences.

    Kind regards, The Access Team
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    Copyright 2022 Prakhar Trivedi
    """.format(targetIdentity['username'], otp)

    html = render_template('emails/confirmEmailUpdate.html', username=targetIdentity['username'], otpCode=otp)

    Emailer.sendEmail(request.json['newEmail'], "Confirm Email Update | Access Portal", text, html)

    Logger.log("API CONFIRMEMAILUPDATE: Sent OTP verification email for email update attempt of identity '{}'.".format(targetIdentity['username']))

    ## Update Access Analytics
    response = AccessAnalytics.newEmail(request.json['newEmail'], text, "Confirm Email Update | Access Portal", targetIdentity['username'])
    if isinstance(response, str):
        if response.startswith("AAError:"):
            print("API: There was an error in updating Analytics with new email data; Response: {}".format(response))
        else:
            print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))
    elif isinstance(response, bool) and response == True:
        print("API: Successfully updated Analytics with new email data.")
    else:
        print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))

    return "SUCCESS: Email confirmation email was sent to {}".format(request.json['newEmail'])


@apiBP.route('/api/updateIdentityEmail', methods=['POST'])
def updateIdentityEmail():
    global accessIdentities
    global validOTPCodes

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'newEmail' not in request.json:
        return "ERROR: Invalid request body."
    if 'currentPass' not in request.json:
        return "ERROR: Invalid request body."
    if 'certID' not in request.json:
        return "ERROR: Invalid request body."
    if 'otpCode' not in request.json:
        return "ERROR: Invalid request body."

    ## Get identity from certID
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."

    ## Check current password
    if not Encryption.verifySHA256(request.json['currentPass'], targetIdentity['password']):
        Logger.log("API UPDATEIDENTITYEMAIL: Blocked unauthorised attempt to update email for identity '{}'.".format(targetIdentity['username']))
        return "UERROR: Password is incorrect."

    ## Check if it is a valid email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", request.json['newEmail']):
        return "UERROR: That is not a valid email."

    for username in accessIdentities:
        if accessIdentities[username]['email'] == request.json['newEmail']:
            return "UERROR: That email is already taken."

    ## Check if email was sent an OTP code
    if request.json['newEmail'] not in validOTPCodes:
        return "ERROR: No OTP code was sent to that email. Please make a request to send an OTP verification email first."

    ## Check OTP code
    if validOTPCodes[request.json['newEmail']] != request.json['otpCode']:
        Logger.log("API UPDATEIDENTITYEMAIL: Blocked unauthorised attempt to update email for identity '{}'.".format(targetIdentity['username']))
        return "UERROR: OTP Code is incorrect."

    # Update Access Identity's email, update database, delete otp code, return success response
    accessIdentities[targetIdentity['username']]['email'] = request.json['newEmail']
    with open('accessIdentities.txt', 'w') as f:
        json.dump(accessIdentities, f)

    validOTPCodes.pop(request.json['newEmail'])
    with open('validOTPCodes.txt', 'w') as f:
        json.dump(validOTPCodes, f)

    Logger.log("API UPDATEIDENTITYEMAIL: Updated email for identity '{}'.".format(targetIdentity['username']))

    return "SUCCESS: Email for Access Identity successfully updated."

@apiBP.route('/api/updateIdentityPassword', methods=['POST'])
def updateIdentityPassword():
    global accessIdentities
    
    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'certID' not in request.json:
        return "ERROR: Invalid request body."
    if 'currentPass' not in request.json:
        return "ERROR: Invalid request body."
    if 'newPass' not in request.json:
        return "ERROR: Invalid request body."

    ## Verify certID and obtain target identity
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."
    
    ## Check currentPass
    if not Encryption.verifySHA256(request.json['currentPass'], targetIdentity['password']):
        Logger.log("API UPDATEIDENTITYPASSWORD: Blocked unauthorised attempt to change password for identity '{}' due to invalid current password.".format(targetIdentity['username']))
        return "UERROR: Current password is incorrect."

    ## Check if password is secure enough
    specialCharacters = list('!@#$%^&*()_-+')

    hasSpecialChar = False
    hasNumericDigit = False
    for char in request.json['newPass']:
        if char.isdigit():
            hasNumericDigit = True
        elif char in specialCharacters:
            hasSpecialChar = True

    if not (hasSpecialChar and hasNumericDigit):
        return "UERROR: Password must have at least 1 special character and 1 numeric digit."

    # Update access identity with password, send password update email, update db, return success response
    hashedNewPass = Encryption.encodeToSHA256(request.json['newPass'])
    accessIdentities[targetIdentity['username']]['password'] = hashedNewPass
    with open('accessIdentities.txt', 'w') as f:
        json.dump(accessIdentities, f)

    targetIdentity['password'] = hashedNewPass

    Logger.log("API UPDATEIDENTITYPASSWORD: Updated password for identity '{}'.".format(targetIdentity['username']))

    ## Send email
    text = """
    Hi {},

    This is an alert to notify that you have successfully changed you Access Identity's password as of {} on the Access Portal. You can change your password again any time in the Identity Information & Management
    (IIM) Settings pane.

    Wasn't you? Click on this link to reset your password so as to recover your identity: {}

    Thank you for your time!

    Kind Regards,
    The Access Team

    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    Copyright 2022 Prakhar Trivedi
    """.format(
        targetIdentity['username'], 
        datetime.datetime.now().strftime(Universal.systemWideStringDateFormat) + ' UTC' + time.strftime('%z'), 
        request.host_url + url_for('identityMeta.passwordReset')[1::]
    )

    html = render_template(
        'emails/passwordUpdated.html', 
        username=targetIdentity['username'],
        resetPwdLink=(request.host_url + url_for('identityMeta.passwordReset')[1::]),
        timestamp=datetime.datetime.now().strftime(Universal.systemWideStringDateFormat) + ' UTC' + time.strftime('%z')
        )

    ## Actually send and update analytics
    Emailer.sendEmail(targetIdentity['email'], "Password Updated | Access Portal", text, html)

    ## Update Access Analytics
    response = AccessAnalytics.newEmail(targetIdentity['email'], text, "Password Updated | Access Portal", targetIdentity['username'])
    if isinstance(response, str):
        if response.startswith("AAError:"):
            print("API: There was an error in updating Analytics with new email data; Response: {}".format(response))
        else:
            print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))
    elif isinstance(response, bool) and response == True:
        print("API: Successfully updated Analytics with new email data.")
    else:
        print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))

    return "SUCCESS: Password successfully updated."

@apiBP.route('/api/deleteIdentity', methods=['POST'])
def deleteIdentity():
    global accessIdentities
    global validOTPCodes
    
    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'certID' not in request.json:
        return "ERROR: Invalid request body."
    if 'authToken' not in request.json:
        return "ERROR: Invalid request body."
    if 'currentPass' not in request.json:
        return "ERROR: Invalid request body."
    
    # Verify certificate ID and get identity based on it
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: Certificate ID provided is not associated with any Access Identity."
    
    # Verify auth token
    if 'loggedInAuthToken' not in targetIdentity:
        Logger.log("API DELETEIDENTITY: Blocked delete identity attempt for '{}' due to no active login session.".format(targetIdentity['username']))
        return "UERROR: Your login session has expired. Please re-login."
    if targetIdentity['loggedInAuthToken'] != request.json['authToken']:
        Logger.log("API DELETEIDENTITY: Blocked delete identity attempt for '{}' due to invalid auth token.".format(targetIdentity['username']))
        return "UERROR: Invalid credentials. Request failed."
    
    # Verify current password
    if not Encryption.verifySHA256(request.json['currentPass'], targetIdentity['password']):
        Logger.log("API DELETEIDENTITY: Blocked delete identity attempt for '{}' due to incorrect password.".format(targetIdentity['username']))
        return "UERROR: Password is incorrect."
    
    # DELETE ALL RECORDS

    ## possible validOTPCode entries
    if targetIdentity['email'] in validOTPCodes:
        validOTPCodes.pop(targetIdentity['email'])

    ## Delete certificate
    response = CertAuthority.permanentlyDeleteCertificate(targetIdentity['associatedCertID'])
    if CAError.checkIfErrorMessage(response) or response != "Successfully deleted that certificate.":
        Logger.log("API DELETEIDENTITY SYSTEMERROR: Error response received from CA when attempting to delete certificate for identity '{}': {}".format(targetIdentity['username'], response))
        return "SYSTEMERROR: An internal error occurred. Please try again."
    
    ## Delete Access Folder
    if AFManager.checkIfFolderIsRegistered(targetIdentity['username']):
        afmResponse = AFManager.deleteFolder(targetIdentity['username'])
        if AFMError.checkIfErrorMessage(afmResponse):
            Logger.log("API DELETEIDENTITY SYSTEMERROR: Error response received from AFM when attempting to delete Access Folder for identity '{}': {}".format(targetIdentity['username'], afmResponse))
            return "SYSTEMERROR: An internal error occurred. Please try again."
    
    ## Delete identity records
    try:
        accessIdentities.pop(targetIdentity['username'])
    except Exception as e:
        Logger.log("API DELETEIDENTITY SYSTEMERROR: Error in deleting records for identity '{}': {}".format(targetIdentity['username'], e))
        return "SYSTEMERROR: An internal error occurred. Please try again."

    ## SAVE ALL CHANGES TO DATABASE
    try:
        with open('validOTPCodes.txt', 'w') as f:
            json.dump(validOTPCodes, f)
    except Exception as e:
        Logger.log("API DELETEIDENTITY SYSTEMERROR: Failed to sync deletion of entries associated with identity '{}' to OTP database; error: {}".format(targetIdentity['username'], e))
        return "SYSTEMERROR: An internal error occurred. Please try again."

    try:
        with open('accessIdentities.txt', 'w') as f:
            json.dump(accessIdentities, f)
    except Exception as e:
        Logger.log("API DELETEIDENTITY SYSTEMERROR: Failed to sync deletion of '{}' to identities database; error: {}".format(e))
        return "SYSTEMERROR: An internal error occurred. Please try again."

    try:
        savingDeletionCAResponse = CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))
        if CAError.checkIfErrorMessage(savingDeletionCAResponse):
            Logger.log("API DELETEIDENTITY SYSTEMERROR: Error response received from CA when attempting to sync deletion of certificate for identity '{}' to database; response: {}".format(targetIdentity['username'], savingDeletionCAResponse))
            return "SYSTEMERROR: An internal error occurred. Please try again."
    except Exception as e:
        Logger.log("API DELETEIDENTITY SYSTEMERROR: Error in deleting certificate of identity '{}' from database; error: {}".format(targetIdentity['username'], e))
        return "SYSTEMERROR: An internal error occurred. Please try again."
    
    # Update Access Analytics
    aaResponse = AccessAnalytics.newIdentityDeletion()
    
    if isinstance(aaResponse, str):
        if aaResponse.startswith("AAError"):
            print("API: Failed to update Access Analytics with new identity deletion; Response: {}".format(aaResponse))
        else:
            print("API: Unknown string response received from Access Analytics when attempting to update with new identity deletion; Response: {}".format(aaResponse))
    elif aaResponse != True:
        print("API: Unknown response received from Access Analytics when attempting to update with new identity deletion; Response: {}".format(aaResponse))
    else:
        print("API: Updated Access Analytics with new identity deletion.")

    Logger.log("API DELETEIDENTITY: Successfully deleted identity '{}'.".format(targetIdentity['username']))

    return "SUCCESS: Identity was successfully wiped from system."

@apiBP.route('/api/sendResetKey', methods=['POST'])
def sendResetKey():
    global accessIdentities
    global validOTPCodes

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'identityEmail' not in request.json:
        return "ERROR: Invalid request body."

    # Verify email
    emails = [accessIdentities[user]['email'] for user in accessIdentities]
    if request.json['identityEmail'] not in emails:
        return "UERROR: Email provided is not associated with any Access Identity."

    # Generate reset key
    options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    resetKey = ''
    for i in range(5):
        resetKey += random.choice(options)

    # Update identity data
    targetIdentity = obtainTargetIdentity(request.json['identityEmail'], accessIdentities)
    identityUsername = targetIdentity['username']

    accessIdentities[identityUsername]['resetKey'] = {
        "key": resetKey,
        "datetime": datetime.datetime.now().strftime(Universal.systemWideStringDateFormat)
    }
    with open('accessIdentities.txt', 'w') as f:
        json.dump(accessIdentities, f)

    # Send reset key in email
    text = """
    Hi {},

    You recently requested to reset your identity's password on the Access Portal. For verification, please enter the password reset key below onto the portal to complete your password reset.

    Password Reset Key: {}

    Please note that this key is only valid for 15 minutes; after which, you will get an invalid key error when attempting to complete your password reset.

    Kind Regards,
    The Access Team

    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    Copyright 2022 Prakhar Trivedi
    """.format(identityUsername, resetKey)

    html = render_template(
        'emails/passwordResetKey.html', 
        username=identityUsername,
        resetKey=resetKey
        )

    ## Actually send and update analytics
    Emailer.sendEmail(targetIdentity['email'], "Password Reset Key | Access Portal", text, html)

    Logger.log("API SENDRESETKEY: Reset key sent to email associated with identity '{}'.".format(identityUsername))

    ## Update Access Analytics
    response = AccessAnalytics.newEmail(targetIdentity['email'], text, "Password Reset Key | Access Portal", identityUsername)
    if isinstance(response, str):
        if response.startswith("AAError:"):
            print("API: There was an error in updating Analytics with new email data; Response: {}".format(response))
        else:
            print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))
    elif isinstance(response, bool) and response == True:
        print("API: Successfully updated Analytics with new email data.")
    else:
        print("API: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))

    return "SUCCESS: Reset key was successfully sent to the identity's email."

@apiBP.route('/api/resetPassword', methods=['POST'])
def resetPassword():
    global accessIdentities
    global validOTPCodes

    # Expire any reset keys that are older than 15 minutes
    for username in accessIdentities:
        if 'resetKey' in accessIdentities[username]:
            if (datetime.datetime.now() - datetime.datetime.strptime(accessIdentities[username]['resetKey']['datetime'], Universal.systemWideStringDateFormat)) > datetime.timedelta(minutes=15):
                del accessIdentities[username]['resetKey']

    with open('accessIdentities.txt', 'w') as f:
        json.dump(accessIdentities, f)

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'identityEmail' not in request.json:
        return "ERROR: Invalid request body."
    if 'resetKey' not in request.json:
        return "ERROR: Invalid request body."
    if 'newPassword' not in request.json:
        return "ERROR: Invalid request body."

    # Verify email
    emails = [accessIdentities[user]['email'] for user in accessIdentities]
    if request.json['identityEmail'] not in emails:
        return "UERROR: Email provided is not associated with any Access Identity."

    # Verify reset key
    targetIdentity = obtainTargetIdentity(request.json['identityEmail'], accessIdentities)
    identityUsername = targetIdentity['username']
    if 'resetKey' not in targetIdentity:
        Logger.log("API RESETPASSWORD: Blocked reset password attempt for identity '{}' due to no/expired reset key sent to associated email.".format(identityUsername))
        return "UERROR: No reset key was sent to this identity. If you did get a reset key email, the key may have expired if you are entering it more than 15 minutes after the reset key email was sent to you."
    if targetIdentity['resetKey']['key'] != request.json['resetKey']:
        Logger.log("API RESETPASSWORD: Blocked reset password attempt for identity '{}' due to incorrect reset key.".format(identityUsername))
        return "UERROR: Reset key is incorrect."
    
    ## Check if password is secure enough
    specialCharacters = list('!@#$%^&*()_-+')

    hasSpecialChar = False
    hasNumericDigit = False
    for char in request.json['newPassword']:
        if char.isdigit():
            hasNumericDigit = True
        elif char in specialCharacters:
            hasSpecialChar = True

    if not (hasSpecialChar and hasNumericDigit):
        return "UERROR: Password must have at least 1 special character and 1 numeric digit."

    # Update identity data
    accessIdentities[identityUsername]['password'] = Encryption.encodeToSHA256(request.json['newPassword'])
    del accessIdentities[identityUsername]['resetKey']

    ## Logout instances of user if they are logged in for security
    if 'loggedInAuthToken' in accessIdentities[identityUsername]:
        del accessIdentities[identityUsername]['loggedInAuthToken']
    
    with open('accessIdentities.txt', 'w') as f:
        json.dump(accessIdentities, f)

    Logger.log("API RESETPASSWORD: Reset password for identity '{}' successful. Any existing login session has been de-activated.".format(identityUsername))

    return "SUCCESS: Password was successfully reset."