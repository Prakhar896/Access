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
            "logoutLink": request.host_url + "identity/logout?authToken={}&username={}".format(authToken, check[1]),
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
            if filenames == []:
                return render_template('portal/portalFolder.html', slotsAvailable=3, files=None, username=check[1], url=request.url)
            else:
                slotsAvailable = 3 - len(filenames)
                return render_template('portal/portalFolder.html', slotsAvailable=slotsAvailable, files=filenames, url=request.url, username=check[1])
        else:
            return render_template("portal/folderRegistration.html", username=check[1])
    else:
        return check

@app.route('/portal/session/<certID>/<authToken>/folder/newUpload', methods=['GET', 'POST'])
def newUpload(certID, authToken):
    check = checkSessionCredentials(certID, authToken)

    if isinstance(check, list) and check[0]:
        if AFManager.checkIfFolderIsRegistered(username=check[1]):
            if request.method == 'POST':
                # check if the post request has the file part
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['file']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    if len(AFManager.getFilenames(username=check[1])) < 3:
                        filename = secure_filename(file.filename)
                        app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'AccessFolders', check[1])
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        return redirect(url_for('download_file', name=filename, certID=certID, authToken=authToken))
                    else:
                        flash("No file slots available.")
                        return redirect(request.url)
                else:
                    flash('Filename is not allowed. Please try again.')
                    return redirect(request.url)
            if (3 - len(AFManager.getFilenames(username=check[1]))) == 0:
                return redirect(url_for('portalFolder', certID=certID, authToken=authToken))
            return render_template('portal/newUpload.html', slotsAvailable=(3 - len(AFManager.getFilenames(check[1]))))
        else:
            return redirect(url_for('portalFolder', certID=certID, authToken=authToken))
    else:
        return check

@app.route('/portal/session/<certID>/<authToken>/folder/uploads/<name>')
def download_file(certID, authToken, name):
    check = checkSessionCredentials(certID, authToken)
    if isinstance(check, list) and check[0]:
        if AFManager.checkIfFolderIsRegistered(username=check[1]):
            app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'AccessFolders', check[1])
            return send_from_directory(app.config["UPLOAD_FOLDER"], name)
        else:
            return redirect(url_for('portalFolder', certID=certID, authToken=authToken))
    else:
        return check
