from flask import redirect, url_for
from main import *


def checkSessionCredentials(certID, authToken):
    CertAuthority.expireOldCertificates()
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))
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
        return render_template('portal/portalHome.html', username=check[1])
    else:
        return check
