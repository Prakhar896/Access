from main import *

@app.route('/api/createIdentity', methods=['POST'])
def makeAnIdentity():
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
    CertAuthority.expireOldCertificatesAndSaveToFile()
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))

    if 'Content-Type' not in request.headers:
        return "ERROR: Content-Type header not present in API request. Request failed."
    if 'AccessAPIKey' not in request.headers:
        return "ERROR: AccessAPIKey header not present in API request. Request failed."
    if request.headers['Content-Type'] != 'application/json':
        return "ERROR: Content-Type header had incorrect value for this API request (expected application/json). Request failed."
    if request.headers['AccessAPIKey'] != os.environ['AccessAPIKey']:
        return "ERROR: Incorrect AccessAPIKey value for this API request. Request failed."

    if 'email' not in request.json:
        return "ERROR: email field not present in body. Request failed."
    if 'password' not in request.json:
        return "ERROR: password field not present in body. Request failed."

    targetIdentity = {}
    for username in accessIdentities:
        if accessIdentities[username]['email'] == request.json['email']:
            targetIdentity = accessIdentities[username]
            targetIdentity["username"] = username
    
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
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))
    return "SUCCESS: Identity logged in."
