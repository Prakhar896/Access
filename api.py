from main import *
from models import *
import re

def headersCheck(headers):
    ## Headers check
    if 'Content-Type' not in headers:
        return "ERROR: Content-Type header not present in API request. Request failed."
    if 'AccessAPIKey' not in headers:
        return "ERROR: AccessAPIKey header not present in API request. Request failed."

    if headers['Content-Type'] != 'application/json':
        return "ERROR: Content-Type header had incorrect value for this API request (expected application/json). Request failed."
    if headers['AccessAPIKey'] != os.environ['AccessAPIKey']:
        return "ERROR: Incorrect AccessAPIKey value for this API request. Request failed."

    return True

@app.route('/api/createIdentity', methods=['POST'])
def makeAnIdentity():
    global validOTPCodes
    global accessIdentities
    if 'Content-Type' not in request.headers or 'AccessAPIKey' not in request.headers:
        return "ERROR: One or more headers were not present in the API request. Request failed."
    if request.headers['Content-Type'] == 'application/json' and request.headers['AccessAPIKey'] == os.environ['AccessAPIKey']:
        if 'username' not in request.json:
            return "ERROR: New identity username field not present in body. Request failed."
        if 'password' not in request.json:
            return "ERROR: New identity password field not present in body. Request failed."
        if 'email' not in request.json:
            return "ERROR: New identity email field not present in body. Request failed."
        if 'otpCode' not in request.json:
            return "ERROR: New identity OTP field not present in body. Request failed."

        # Check if username is already taken
        if request.json['username'] in accessIdentities:
            return "UERROR: Username already taken."
        
        # Check if email is already taken
        if request.json['email'] in accessIdentities:
            return "UERROR: Email already taken."

        # Check if otp code is valid
        if request.json['email'] not in validOTPCodes:
            return "ERROR: OTP code could not be verified as email associated with code was not in database. This is likely due to a missing OTP email request. Request failed."
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
        json.dump(validOTPCodes, open('validOTPCodes.txt', 'w'))

        # Create new identity
        accessIdentities[request.json['username']] = {
            'password': CertAuthority.encodeToB64(request.json['password']),
            'email': request.json['email'],
            'otpCode': request.json['otpCode'],
            'sign-up-date': datetime.datetime.now().strftime(systemWideStringDateFormat),
            'last-login-date': datetime.datetime.now().strftime(systemWideStringDateFormat),
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

        return "SUCCESS: Identity created."
    else:
        return "ERROR: One or more of the request headers had incorrect values for this request. Request failed."

@app.route('/api/loginIdentity', methods=['POST'])
def loginIdentity():
    global accessIdentities
    CertAuthority.expireOldCertificates()
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))

    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    if 'email' not in request.json:
        return "ERROR: email field not present in body. Request failed."
    if 'password' not in request.json:
        return "ERROR: password field not present in body. Request failed."

    targetIdentity = obtainTargetIdentity(request.json['email'], accessIdentities)
    
    if targetIdentity == {}:
        return "UERROR: Email not associated with any Access Identity."
    
    if CertAuthority.decodeFromB64(targetIdentity["password"]) != request.json['password']:
        return "UERROR: Password is incorrect."
    
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

    accessIdentities[targetIdentity['username']]['last-login-date'] = datetime.datetime.now().strftime(systemWideStringDateFormat)
    accessIdentities[targetIdentity['username']]['loggedInAuthToken'] = generateAuthToken()
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

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
        datetime=datetime.datetime.now().strftime(systemWideStringDateFormat) + ' UTC' + time.strftime('%z'), 
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
    
@app.route('/api/registerFolder', methods=['POST'])
def registerFolder():
    global accessIdentities

    ## Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Data body check
    if 'username' not in request.json:
        return "ERROR: Username field not present in JSON body of request."
    if request.json['username'] not in accessIdentities:
        return "ERROR: Username not associated with any Access Identity."
    
    ## Folder already exists check
    if AFManager.checkIfFolderIsRegistered(request.json['username']):
        return "ERROR: Folder for the Access Identity is already registered."
    
    ## Checks completed

    ## Register folder under username
    AFManager.registerFolder(request.json['username'])

    ## Send email

    text = """
    Hi {},

    Congratulations on registering your Access Folder! You can now upload upto a maximum of 3 files, each not bigger than 16MB in size that have the following allowed file extensions:
    {}

    Kind Regards,
    The Access Team

    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    Copyright 2022 Prakhar Trivedi
    """.format(request.json['username'], prepFileExtensions)

    html = render_template('emails/folderRegistered.html', username=request.json['username'], fileExtensions=prepFileExtensions)

    ## Send email
    Emailer.sendEmail(accessIdentities[request.json['username']]['email'], "Access Folder Registered!", text, html)

    ## Update Access Identity
    accessIdentities[request.json['username']]['folderRegistered'] = True

    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

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

@app.route('/api/logoutIdentity', methods=['POST'])
def logoutIdentity():
    global accessIdentities

    # Headers Check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check
    
    # Body check
    if 'username' not in request.json:
        return "ERROR: Username field not present in request body."
    if 'authToken' not in request.json:
        return "ERROR: Auth Token field not present in request body."
    if request.json['username'] not in accessIdentities:
        return "UERROR: Given username is not associated with any Access Identity."
    if 'loggedInAuthToken' not in accessIdentities[request.json['username']]:
        return "UERROR: Access Identity is not logged in. Only logged in identities can be logged out."
    if request.json['authToken'] != accessIdentities[request.json['username']]['loggedInAuthToken']:
        return "UERROR: Auth token does not match with the one associated with the logged in identity."
    
    # Logout process
    try:
        del accessIdentities[request.json['username']]['loggedInAuthToken']
        json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

        ## Update Access Analytics
        response = AccessAnalytics.newSignout()
        if isinstance(response, str):
            if response.startswith("AAError:"):
                print("API: Error in updating Analytics with new sign out; Response: {}".format(response))
            else:
                print("API: Unexpected response when attempting to update Analytics with new sign out; Response: {}".format(response))

    except Exception as e:
        print("API: An error occurred in logging out user {}: {}".format(request.json['username'], e))
        return "ERROR: An error occurred in logging out: {}".format(e)
    
    return "SUCCESS: Logged out user {}.".format(request.json['username'])

@app.route('/api/deleteFile', methods=['POST'])
def deleteFileFromFolder():
    global accessIdentities

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'username' not in request.json:
        return "ERROR: Username field is not present in request body."
    if request.json['username'] not in accessIdentities:
        return "UERROR: Username is not associated with any Access Identity. Please try again."
    if 'filename' not in request.json:
        return "ERROR: Filename field is not present in request body."

    if not AFManager.checkIfFolderIsRegistered(username=request.json['username']):
        return "UERROR: Folder for the Access Identity associated with that username has not been registered."
    
    files = AFManager.getFilenames(username=request.json['username'])

    if request.json['filename'] not in files:
        return "UERROR: No such file exists under your Access Folder."
    
    # Deletion of file

    response = AFManager.deleteFile(username=request.json['username'], filename=request.json['filename'])
    if AFMError.checkIfErrorMessage(response):
        return "ERROR: {}".format(response)
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
            print("API: When updating Access Identity with file deletion, file's name was not found in the identity. Recovering and continuing...")

        json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

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

@app.route('/api/userPreferences', methods=["POST"])
def fetchUserPreferences():
    global accessIdentities

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'certID' not in request.json:
        return "ERROR: Field 'certID' is not present in request body."
    
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."
    
    if 'resourceReq' not in request.json:
        return "ERROR: Field 'resourceReq' is not present in request body."
    if request.json['resourceReq'] not in ['emailPrefs']:
        return "ERROR: Invalid resource was requested."

    # Response to request
    if request.json['resourceReq'] == 'emailPrefs':
        responseObject = copy.deepcopy(targetIdentity['settings']['emailPref'])
        responseObject['responseStatus'] = "SUCCESS"
        return responseObject

@app.route('/api/updateUserPreference', methods=['POST'])
def updateUserPreference():
    global accessIdentities

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'certID' not in request.json:
        return "ERROR: Field 'certID' is not present in request body."
    
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."
    
    if 'resourceReq' not in request.json:
        return "ERROR: Field 'resourceReq' is not present in request body."
    if request.json['resourceReq'] not in ['emailPrefs', 'certData', 'identityInfo']:
        return "ERROR: Invalid resource was requested."

    if 'preferenceName' not in request.json:
        return "ERROR: Field 'preferenceName' not present in request body."

    if 'newValue' not in request.json:
        return "ERROR: Field 'newValue' not present in request body."
    
    ## Update preference and respond
    if request.json['resourceReq'] == "emailPrefs":
        if request.json["preferenceName"] not in ['loginNotifs', 'fileUploadNotifs', 'fileDeletionNotifs']:
            return "ERROR: Given preference name for that settings resource does not exist."

        accessIdentities[targetIdentity['username']]['settings']['emailPref'][request.json['preferenceName']] = request.json['newValue']
        targetIdentity['settings']['emailPref'][request.json['preferenceName']] = request.json['newValue']

        json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

        responseObject = copy.deepcopy(targetIdentity['settings']['emailPref'])
        responseObject['responseStatus'] = "SUCCESS"

        return responseObject

@app.route('/api/confirmEmailUpdate', methods=['POST'])
def confirmEmailUpdate():
    global accessIdentities
    global validOTPCodes

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'newEmail' not in request.json:
        return "ERROR: 'newEmail' field not present in request body."
    if 'currentPass' not in request.json:
        return "ERROR: Current password field not present in request body."
    if 'certID' not in request.json:
        return "ERROR: Certificate ID field not present in request body."

    ## Get identity from certID
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."

    ## Check current password
    decodedPass = CertAuthority.decodeFromB64(targetIdentity['password'])
    if decodedPass != request.json['currentPass']:
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
    json.dump(validOTPCodes, open('validOTPCodes.txt', 'w'))

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


@app.route('/api/updateIdentityEmail', methods=['POST'])
def updateIdentityEmail():
    global accessIdentities
    global validOTPCodes

    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'newEmail' not in request.json:
        return "ERROR: 'newEmail' field not present in request body."
    if 'currentPass' not in request.json:
        return "ERROR: Current password field not present in request body."
    if 'certID' not in request.json:
        return "ERROR: Certificate ID field not present in request body."
    if 'otpCode' not in request.json:
        return "ERROR: OTP Code field not present in request body."

    ## Get identity from certID
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."

    ## Check current password
    decodedPass = CertAuthority.decodeFromB64(targetIdentity['password'])
    if decodedPass != request.json['currentPass']:
        return "UERROR: Password is incorrect."

    ## Check if it is a valid email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", request.json['newEmail']):
        return "UERROR: That is not a valid email."

    for username in accessIdentities:
        if accessIdentities[username]['email'] == request.json['newEmail']:
            return "UERROR: That email is already taken."

    ## Check if email was sent an OTP code
    if request.json['newEmail'] not in validOTPCodes:
        return "ERROR: No OTP code was sent to that email. Please send a confirmEmailUpdate POST request to send an OTP to the new email first."

    ## Check OTP code
    if validOTPCodes[request.json['newEmail']] != request.json['otpCode']:
        return "UERROR: OTP Code is incorrect."

    # Update Access Identity's email, update database, delete otp code, return success response
    accessIdentities[targetIdentity['username']]['email'] = request.json['newEmail']
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

    validOTPCodes.pop(request.json['newEmail'])
    json.dump(validOTPCodes, open('validOTPCodes.txt', 'w'))

    return "SUCCESS: Email for Access Identity successfully updated."

@app.route('/api/updateIdentityPassword', methods=['POST'])
def updateIdentityPassword():
    global accessIdentities
    
    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'certID' not in request.json:
        return "ERROR: Certificate ID field not present in request body."
    if 'currentPass' not in request.json:
        return "ERROR: Current password field not present in request body."
    if 'newPass' not in request.json:
        return "ERROR: New password field not present in request body."

    ## Verify certID and obtain target identity
    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == request.json['certID']:
            targetIdentity = copy.deepcopy(accessIdentities[username])
            targetIdentity['username'] = username
    
    if targetIdentity == {}:
        return "ERROR: No such Access Identity is associated with that certificate ID."
    
    ## Check currentPass
    if request.json['currentPass'] != CertAuthority.decodeFromB64(targetIdentity['password']):
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
    accessIdentities[targetIdentity['username']]['password'] = CertAuthority.encodeToB64(request.json['newPass'])
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

    targetIdentity['password'] = CertAuthority.encodeToB64(request.json['newPass'])

    ## Send email
    text = """
    Hi {},

    This is an alert to notify that you have successfully changed you Access Identity's password as of {} on the Access Portal. You can change your password again any time in the Identity Information & Management
    (IIM) Settings pane.

    Thank you for your time!

    Kind Regards,
    The Access Team

    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    Copyright 2022 Prakhar Trivedi
    """.format(targetIdentity['username'], datetime.datetime.now().strftime(systemWideStringDateFormat) + ' UTC' + time.strftime('%z'))

    html = render_template(
        'emails/passwordUpdated.html', 
        username=targetIdentity['username'], 
        timestamp=datetime.datetime.now().strftime(systemWideStringDateFormat) + ' UTC' + time.strftime('%z')
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

@app.route('/api/deleteIdentity', methods=['POST'])
def deleteIdentity():
    global accessIdentities
    global validOTPCodes
    
    # Headers check
    check = headersCheck(headers=request.headers)
    if check != True:
        return check

    # Body check
    if 'certID' not in request.json:
        return "ERROR: Certificate ID field not present in request body."
    if 'authToken' not in request.json:
        return "ERROR: Auth token field not present in request body."
    if 'currentPass' not in request.json:
        return "ERROR: Current password field not present in request body."
    
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
        return "UERROR: Your login session has expired. Please re-login into your identity. (Auth token is invalid)"
    if targetIdentity['loggedInAuthToken'] != request.json['authToken']:
        return "UERROR: Auth token provided does not match with the one associated with the logged in identity."
    
    # Verify current password
    if request.json['currentPass'] != CertAuthority.decodeFromB64(targetIdentity['password']):
        return "UERROR: Password is incorrect."
    
    # DELETE ALL RECORDS

    ## possible validOTPCode entries
    if targetIdentity['email'] in validOTPCodes:
        validOTPCodes.pop(targetIdentity['email'])

    ## Delete certificate
    response = CertAuthority.permanentlyDeleteCertificate(targetIdentity['associatedCertID'])
    if CAError.checkIfErrorMessage(response):
        return "SYSTEMERROR: Error response received from CA when attempting to delete identity certificate: {}".format(response)
    elif response != "Successfully deleted that certificate.":
        return "SYSTEMERROR: An unknown response string was received from CA when attempting to delete identity certificate: {}".format(response)
    
    ## Delete Access Folder
    if AFManager.checkIfFolderIsRegistered(targetIdentity['username']):
        afmResponse = AFManager.deleteFolder(targetIdentity['username'])
        if AFMError.checkIfErrorMessage(afmResponse):
            return "SYSTEMERROR: Error response received from AFM when attempting to delete identity's Access Folder: {}".format(afmResponse)
    
    ## Delete identity records
    try:
        accessIdentities.pop(targetIdentity['username'])
    except Exception as e:
        return "SYSTEMERROR: An error occurred in deleting identity records: {}".format(e)

    ## SAVE ALL CHANGES TO DATABASE
    try:
        json.dump(validOTPCodes, open('validOTPCodes.txt', 'w'))
    except Exception as e:
        return "SYSTEMERROR: Failed to update OTP codes database with deletion of entries associated with the Access Identity; Error: {}".format(e)

    try:
        json.dump(accessIdentities, open('accessIdentities.txt', 'w'))
    except Exception as e:
        return "SYSTEMERROR: Failed to update database with the deletion of the identity's records; Error: {}".format(e)

    try:
        savingDeletionCAResponse = CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))
        if CAError.checkIfErrorMessage(savingDeletionCAResponse):
            return "SYSTEMERROR: Error response received from CA when attempting to save certificate deletion to database: {}".format(savingDeletionCAResponse)
    except Exception as e:
        return "SYSTEMERROR: An error occurred when attempting to update database with the deletion of the identity's certificate; Error: {}".format(e)    
    
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

    return "SUCCESS: Identity was successfully wiped from system."