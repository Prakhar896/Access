from main import *


def checkSessionCredentials(certID, authToken):
    global accessIdentities
    CertAuthority.expireOldCertificates()
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))
    tempIdentities = accessIdentities
    accessIdentities = expireAuthTokens(tempIdentities)
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

    for username in accessIdentities:
        if accessIdentities[username]['associatedCertID'] == certID:
            targetCertificate = CertAuthority.getCertificate(certID)
            if targetCertificate == None:
                return render_template('unauthorised.html', message="No such Access Identity certificate was found.")

            if targetCertificate['revoked'] == True:
                return render_template('unauthorised.html', message="Your Access Identity's Certificate has been revoked. Reason: {}".format(targetCertificate['revocationReason']))
            
            response = CertAuthority.checkCertificateSecurity(targetCertificate)
            if CAError.checkIfErrorMessage(response):
                return render_template('unauthorised.html', message=response)
            elif response == CAError.validCert:
                if 'loggedInAuthToken' in accessIdentities[username] and accessIdentities[username]['loggedInAuthToken'] == authToken:
                    # return render_template('portalHome.html', username=username)
                    return [True, username, targetCertificate]
                else:
                    return render_template("unauthorised.html", message="Invalid authentication token. Please sign in to your identity first.")
    return render_template('unauthorised.html', message="No such Access Identity certificate was found.")


@app.route('/portal/session/<certID>/<authToken>/home')
def portalHome(certID, authToken):
    check = checkSessionCredentials(certID, authToken)
    if isinstance(check, list) and check[0]:
        timeLeft = ""
        for username in accessIdentities:
            if accessIdentities[username]['loggedInAuthToken'] == authToken:
                numberOfMins = (10800 - (datetime.datetime.now() - datetime.datetime.strptime(accessIdentities[username]['last-login-date'], '%Y-%m-%d %H:%M:%S')).total_seconds()) / 60
                numHours = int(numberOfMins / 60)
                numMinutes = numberOfMins - (60 * numHours)
                timeLeft = "{} Hours and {} Minutes Left".format(str(numHours), str(int(numMinutes)))
                break

        sessionDetails = {
            "logoutLink": request.host_url + "identity/logout?authToken={}".format(authToken),
            "timeLeft": timeLeft,
            "currentToken": authToken
        }
        return render_template('portal/portalHome.html', username=check[1], sessionDetails=sessionDetails, url=request.url)
    else:
        return check

@app.route('/portal/session/<certID>/<authToken>/folder')
def portalFolder(certID, authToken):
    check = checkSessionCredentials(certID, authToken)
    if isinstance(check, list) and check[0]:
        if AFManager.checkIfFolderIsRegistered(username=check[1]):
            filenames = AFManager.getFilenames(check[1])
            if filenames == None:
                return render_template('portal/portalFolder.html', slotsAvailable=3, files=None, username=check[1])
            else:
                slotsAvailable = 3 - len(filenames)
                return render_template('portal/portalFolder.html', slotsAvailable=slotsAvailable, files=filenames, url=request.url, username=check[1])
        else:
            return "Your folder is not registered yet."
    else:
        return check
