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
    """.format(targetIdentity['username'], request.host_url + '/identity/logout?authToken=' + accessIdentities[targetIdentity['username']]['loggedInAuthToken'])

    html = render_template("emails/loginEmail.html", userName=targetIdentity['username'], datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' UTC' + time.strftime('%z'), logoutLink=(request.host_url + 'identity/logout?authToken=' + accessIdentities[targetIdentity['username']]['loggedInAuthToken']))

    Emailer.sendEmail(targetIdentity['email'], "Access Identity Login Alert", text, html)

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
    .txt, .pdf, .png, .jpg, .jpeg, .gif

    Kind Regards,
    The Access Team

    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.
    Copyright 2022 Prakhar Trivedi
    """

    html = render_template('emails/folderRegistered.html', username=request.json['username'])

    Emailer.sendEmail(accessIdentities[request.json['username']]['email'], "Access Folder Registered!", text, html)

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
    except Exception as e:
        print("API: An error occurred in logging out user {}: {}".format(request.json['username'], e))
        return "ERROR: An error occurred in logging out: {}".format(e)
    
    return "SUCCESS: Logged out user {}.".format(request.json['username'])
