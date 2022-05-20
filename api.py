from main import *
from models import *

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
            'sign-up-date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last-login-date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'associatedCertID': CertAuthority.issueCertificate(request.json['username'])['certID']
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

    accessIdentities[targetIdentity['username']]['last-login-date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' UTC' + time.strftime('%z'), 
        logoutLink=("{}/identity/logout?authToken={}&username={}".format(request.host_url, accessIdentities[targetIdentity['username']]['loggedInAuthToken'], targetIdentity['username']))
        )

    ## SEND EMAIL
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

    if 'GitpodEnvironment' in os.environ and os.environ['GitpodEnvironment'] == 'True':
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
        targetIdentity = {}
        for username in accessIdentities:
            if username == request.json['username']:
                targetIdentity = accessIdentities[username]

        if "AF_and_files" not in targetIdentity:
            targetIdentity["AF_and_files"] = {}

        if request.json['filename'] in targetIdentity["AF_and_files"]:
            targetIdentity["AF_and_files"].pop(request.json['filename'])
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

        return "SUCCESS: File {} belonging to user {} was successfully deleted.".format(request.json['filename'], request.json['username'])
    else:
        print("API: Unidentified response received from AFManager when executing delete file function. Response: {}".format(response))
        return "ERROR: Unknown response received from AFManager service. Check server logs for more information."