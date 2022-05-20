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
                return render_template('error.html', message="No such Access Identity certificate was found.")

            if targetCertificate['revoked'] == True:
                return render_template('unauthorised.html', message="Your Access Identity's Certificate has been revoked. Reason: {}".format(targetCertificate['revocationReason']), originURL=request.host_url)
            
            response = CertAuthority.checkCertificateSecurity(targetCertificate)
            if CAError.checkIfErrorMessage(response):
                return render_template('unauthorised.html', message=response, originURL=request.host_url)
            elif response == CAError.validCert:
                if 'loggedInAuthToken' in accessIdentities[username] and accessIdentities[username]['loggedInAuthToken'] == authToken:
                    # return render_template('portalHome.html', username=username)
                    return [True, username, targetCertificate]
                else:
                    return render_template("unauthorised.html", message="Invalid authentication token. Please sign in to your identity first.")
    return render_template('unauthorised.html', message="Certificate ID provided does not match any Access Identity.", originURL=request.host_url)


@app.route('/portal/session/<certID>/<authToken>/home')
def portalHome(certID, authToken):
    global accessIdentities

    check = checkSessionCredentials(certID, authToken)
    if isinstance(check, list) and check[0]:
        timeLeft = ""
        for username in accessIdentities:
            if 'loggedInAuthToken' not in accessIdentities[username]:
                continue
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
            return render_template("portal/folderRegistration.html", username=check[1], fileExtensions=prepFileExtensions)
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

                        ## Update Access Identity
                        uploadDatetime = datetime.datetime.now().strftime(systemWideStringDateFormat)
                        targetIdentity = {}
                        for username in accessIdentities:
                            if username == check[1]:
                                targetIdentity = accessIdentities[username]

                        if "AF_and_files" not in targetIdentity:
                            targetIdentity["AF_and_files"] = {}
                        targetIdentity["AF_and_files"][filename] = uploadDatetime
                        accessIdentities[username] = targetIdentity
                        json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

                        ## Update Access Analytics
                        response = AccessAnalytics.newFileUpload()
                        if isinstance(response, str):
                            if response.startswith("AAError:"):
                                print("PORTAL: Error in updating Analytics with new file upload; Response: {}".format(response))
                            else:
                                print("PORTAL: Unexpected response when attempting to update Analytics with new file upload; Response: {}".format(response))

                        return redirect(url_for('download_file', name=filename, certID=certID, authToken=authToken))
                    else:
                        flash("No file slots available.")
                        return redirect(request.url)
                else:
                    flash('Filename is not allowed. Please try again.')
                    return redirect(request.url)
            if (3 - len(AFManager.getFilenames(username=check[1]))) == 0:
                return redirect(url_for('portalFolder', certID=certID, authToken=authToken))
            return render_template('portal/newUpload.html', slotsAvailable=(3 - len(AFManager.getFilenames(check[1]))), fileExtensions=prepFileExtensions)
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

            ## Update Access Analytics
            response = AccessAnalytics.newFileDownload()
            if isinstance(response, str):
                if response.startswith("AAError:"):
                    print("PORTAL: Error in updating Analytics with new file download; Response: {}".format(response))
                else:
                    print("PORTAL: Unexpected response when attempting to update Analytics with new file download; Response: {}".format(response))

            return send_from_directory(app.config["UPLOAD_FOLDER"], name)
        else:
            return redirect(url_for('portalFolder', certID=certID, authToken=authToken))
    else:
        return check

@app.route('/portal/session/<certID>/<authToken>/folder/deleteListing')
def deleteListing(certID, authToken):
    check = checkSessionCredentials(certID, authToken)

    if isinstance(check, list) and check[0]:
        if AFManager.checkIfFolderIsRegistered(username=check[1]):
            filenames = AFManager.getFilenames(username=check[1])

            if filenames == []:
                filenames = None
                return redirect(url_for('portalFolder', certID=certID, authToken=authToken))

            return render_template('portal/deleteListing.html', files=filenames)
        else:
            return redirect(url_for('portalFolder', certID=certID, authToken=authToken))
    else:
        return check

@app.route('/portal/session/<certID>/<authToken>/folder/deleteFile')
def deleteFileConfirmation(certID, authToken):
    check = checkSessionCredentials(certID, authToken)

    if isinstance(check, list) and check[0]:
        if AFManager.checkIfFolderIsRegistered(username=check[1]):
            if 'filename' not in request.args:
                flash('Filename argument not present in delete file confirmation request. Please try again.')
                return redirect(url_for('processError'))

            storedFilenames = AFManager.getFilenames(username=check[1])

            if request.args['filename'] not in storedFilenames:
                flash('No such file exists with that file name in your Access Folder. Please try again.')
                return redirect(url_for('processError'))
            
            return render_template('portal/portalFolderDeleteFile.html', filename=request.args['filename'], username=check[1])