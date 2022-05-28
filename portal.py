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
                    return render_template("unauthorised.html", message="Invalid authentication token. Please sign in to your identity first.", originURL=request.host_url)
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
    global accessIdentities

    check = checkSessionCredentials(certID, authToken)
    if isinstance(check, list) and check[0]:
        if AFManager.checkIfFolderIsRegistered(username=check[1]):
            filenames = AFManager.getFilenames(check[1])
            if filenames == []:
                return render_template('portal/portalFolder.html', slotsAvailable=3, filesData=None, username=check[1], url=request.url)
            else:
                slotsAvailable = 3 - len(filenames)

                ## Collate files data, aka get filename plus its upload timestamp
                collatedFilesData = {}
                
                ### Get target identity
                targetIdentity = {}
                for username in accessIdentities:
                    if username == check[1]:
                        targetIdentity = accessIdentities[username].copy()
                
                if "AF_and_files" not in targetIdentity:
                    targetIdentity["AF_and_files"] = {}
                    accessIdentities[check[1]]["AF_and_files"] = {}

                    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

                for filename in filenames:
                    if filename not in targetIdentity["AF_and_files"]:
                        collatedFilesData[filename] = "ERROR: Timestamp not found."
                    else:
                        collatedFilesData[filename] = targetIdentity["AF_and_files"][filename]

                
                return render_template('portal/portalFolder.html', slotsAvailable=slotsAvailable, filesData=collatedFilesData, url=request.url, username=check[1])
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
                                targetIdentity = accessIdentities[username].copy()

                        if "AF_and_files" not in targetIdentity:
                            targetIdentity["AF_and_files"] = {}
                            accessIdentities[check[1]]['AF_and_files'] = {}

                        targetIdentity["AF_and_files"][filename] = uploadDatetime
                        accessIdentities[check[1]]['AF_and_files'][filename] = uploadDatetime
                        json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

                        ## Update Access Analytics
                        response = AccessAnalytics.newFileUpload()
                        if isinstance(response, str):
                            if response.startswith("AAError:"):
                                print("PORTAL: Error in updating Analytics with new file upload; Response: {}".format(response))
                            else:
                                print("PORTAL: Unexpected response when attempting to update Analytics with new file upload; Response: {}".format(response))

                        ## Send file upload email

                        text = """
    Hi {},

    This email is a notification that you recently uploaded a file with the name: '{}'.

    If this was you, please ignore this email. If it was not, please login to the Access Portal immediately and change your password.

    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY THE ACCESS PORTAL. DO NOT REPLY TO THIS EMAIL.</p>
    Copyright 2022 Prakhar Trivedi
    """.format(check[1], filename)

                        html = render_template('emails/fileUploaded.html', username=check[1], filename=filename)

                        if 'settings' in targetIdentity and 'emailPref' in targetIdentity['settings'] and targetIdentity['settings']['emailPref']['fileUploadNotifs'] == True:
                            Emailer.sendEmail(targetIdentity['email'], "File Uploaded | Access Portal", text, html)

                            ## Update Access Analytics
                            response = AccessAnalytics.newEmail(accessIdentities[check[1]]['email'], text, "File Uploaded | Access Portal", check[1])
                            if isinstance(response, str):
                                if response.startswith("AAError:"):
                                    print("PORTAL: There was an error in updating Analytics with new email data; Response: {}".format(response))
                                else:
                                    print("PORTAL: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))
                            elif isinstance(response, bool) and response == True:
                                print("PORTAL: Successfully updated Analytics with new email data.")
                            else:
                                print("PORTAL: Unexpected response from Analytics when attempting to update with new email data; Response: {}".format(response))

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
    else:
        return check

### SETTINGS WEBPAGES

@app.route('/portal/session/<certID>/<authToken>/settings/emailPref')
def emailPreferences(certID, authToken):
    check = checkSessionCredentials(certID, authToken)

    if isinstance(check, list) and check[0]:
        return render_template('portal/settings/emailPreferences.html', username=check[1], url=request.url)
    else:
        return check

@app.route('/portal/session/<certID>/<authToken>/settings/certStatus')
def certStatus(certID, authToken):
    global accessIdentities
    check = checkSessionCredentials(certID, authToken)

    if isinstance(check, list) and check[0]:
        ## Prepare certificate information for display

        ## Get certificate
        targetIdentity = {}
        for username in accessIdentities:
            if username == check[1]:
                targetIdentity = accessIdentities[username].copy()

        targetCertificate = CertAuthority.getCertificate(targetIdentity['associatedCertID'])
        if targetCertificate == None:
            flash("Could not get certificate information of identity.")
            return redirect(url_for('processError'))

        ## Information to prepare:
        ## 1) Cert ID, 2) Certificate Validity, 3) Certificate Security, 4) Issue Date, 5) Expiry date, 6) Days till expiry

        # 1)
        certID = targetIdentity['associatedCertID']

        # 2)
        validity = ''
        if targetCertificate['revoked'] == False:
            validity = 'Valid'
        else:
            validity = 'REVOKED! (Your login session will remain active until its time is up)'

        # 3)
        secureOrNot = ''
        certAuthResponse = CertAuthority.checkCertificateSecurity(targetCertificate)
        if certAuthResponse == CAError.validCert:
            secureOrNot = 'Secure 🔒'
        elif CAError.checkIfErrorMessage(certAuthResponse):
            secureOrNot = 'INSECURE! Your cert may have been damaged/manipulated'
        else:
            secureOrNot = 'Security could not be determined'

        # 4)
        issueDate = targetCertificate['issueDate']

        # 5)
        expiryDate = targetCertificate['expiryDate']

        # 6)
        daysTillExpiry = str((datetime.datetime.strptime(expiryDate, systemWideStringDateFormat) - datetime.datetime.now()).days)

        ## Complete date object
        certData = {
            'certID': certID,
            'validity': validity,
            'security': secureOrNot,
            'issueDate': issueDate,
            'expiryDate': expiryDate,
            'daysTillExpiry': daysTillExpiry
        }

        return render_template('portal/settings/certificateStatus.html', username=check[1], url=request.url, certData=certData)
    else:
        return check

@app.route('/portal/session/<certID>/<authToken>/settings/idInfo')
def idInfoAndManagement(certID, authToken):
    global accessIdentities
    check = checkSessionCredentials(certID, authToken)

    if isinstance(check, list) and check[0]:
        
        # Get target identity
        targetIdentity = {}
        for username in accessIdentities:
            if username == check[1]:
                targetIdentity = accessIdentities[username].copy()
        
        # Collate identity information
        AFStatusString = ''

        if targetIdentity['folderRegistered'] == False:
            AFStatusString = 'Access Folder Not Registered'
        else:
            fileSlotsAvailable = 3 - len(targetIdentity['AF_and_files'])
            AFStatusString = 'Registered, {} File Slots Free'.format(fileSlotsAvailable)

        idInfo = {
            'email': targetIdentity['email'],
            'passCensored': '●' * len(CertAuthority.decodeFromB64(targetIdentity['password'])),
            'creationDate': datetime.datetime.strptime(targetIdentity['sign-up-date'], systemWideStringDateFormat).strftime('%d %B, %A, %Y %H:%M:%S%p') + ' UTC' + time.strftime('%z'),
            'AFStatus': AFStatusString
        }

        return render_template('portal/settings/identityInfo.html', username=check[1], url=request.url, idInfo=idInfo)
    else:
        return check