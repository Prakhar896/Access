# Set DeveloperModeEnabled to "True" in .env file to enable the Developer Tools Suite
import time, json, os, datetime, copy
from models import systemWideStringDateFormat
from getpass import getpass
from certAuthority import *
from AFManager import *
from accessAnalytics import *
def toolsStartup():

    print("""
Welcome to the Developer Tools Suite!
(PRO Tip: This suite is displayed because you have enabled Developer Mode
by setting "DeveloperModeEnabled" to "True" in the .env file.)

Options:

        1) Create a new Identity
        2) Delete an Identity
        3) View All Identities and their Data
        4) Cert Authority and Certificates Tools

    """)
    devToolsChoice = int(input("What would you like to do: "))
    print()
    if devToolsChoice == 1:
        # Initiate manual Create identity process; ask user for parameter inputs
        print("Initializing Manual Create Identity Process...Please give inputs as follows...")
        time.sleep(2)

        # Load access identities and certificates
        if not os.path.isfile('accessIdentities.txt'):
            with open('accessIdentities.txt', 'w') as f:
                f.write("{}")

        accessIdentities = json.load(open('accessIdentities.txt', 'r'))

        if not os.path.isfile('certificates.txt'):
            with open('certificates.txt', 'w') as f:
                f_content = """{ "registeredCertificates": {}, "revokedCertificates": {}}"""
                f.write(f_content)

        CAresponse = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
        if CAError.checkIfErrorMessage(CAresponse):
            print("STARTUP CREATE IDENTITY DEV TOOL: Error in loading certificates; response from CA: " + CAresponse)
            sys.exit(1)
        print()

        ## GET INPUTS
        username = input("Enter new identity's username: ")
        while True:
            # Check if username is already taken
            if username in accessIdentities:
                print("ERROR: Username already taken.")
                username = input("Enter new identity's username: ")
                continue
            break

        email = input("Enter new identity's email: ")
        while True:
            # Check if email is already taken
            if email in [accessIdentities[x]['email'] for x in accessIdentities]:
                print("ERROR: Email already taken.")
                email = input("Enter new identity's email: ")
                continue
            break
        
        password = getpass("Enter new identity's password: ")
        # Check if password is secure enough
        specialCharacters = list('!@#$%^&*()_-+')
        while True:
            hasSpecialChar = False
            hasNumericDigit = False
            for char in password:
                if char.isdigit():
                    hasNumericDigit = True
                elif char in specialCharacters:
                    hasSpecialChar = True

            if not (hasSpecialChar and hasNumericDigit):
                print("ERROR: Password must have at least 1 special character and 1 numeric digit.")
                password = getpass("Enter new identity's password: ")
                continue
            break

        ## Gather rest of the inputs
        numbers = [str(i) for i in range(10)]
        otp = ''.join(random.choice(numbers) for i in range(6))

        # Create new identity
        accessIdentities[username] = {
            'password': CertAuthority.encodeToB64(password),
            'email': email,
            'otpCode': otp,
            'sign-up-date': datetime.datetime.now().strftime(systemWideStringDateFormat),
            'last-login-date': datetime.datetime.now().strftime(systemWideStringDateFormat),
            'associatedCertID': CertAuthority.issueCertificate(username)['certID'],
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

        print("DEV TOOLS: Successfully created identity. You may now login with the identity's credentials in the Access Portal.")
    elif devToolsChoice == 2:
        # Initiate manual delete identity
        print("Initializing manual delete identity process...please wait!")
        print()
        time.sleep(3)

        # Load access identities and certificates, valid otp codes, prep AA environment
        if not os.path.isfile('accessIdentities.txt'):
            with open('accessIdentities.txt', 'w') as f:
                f.write("{}")

        accessIdentities = json.load(open('accessIdentities.txt', 'r'))

        if not os.path.isfile('certificates.txt'):
            with open('certificates.txt', 'w') as f:
                f_content = """{ "registeredCertificates": {}, "revokedCertificates": {}}"""
                f.write(f_content)

        CAresponse = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
        if CAError.checkIfErrorMessage(CAresponse):
            print("DELETE IDENTITY DEV TOOL: Error in loading certificates; response from CA: " + CAresponse)
            sys.exit(1)
        print()

        if not os.path.isfile('validOTPCodes.txt'):
            with open('validOTPCodes.txt', 'w') as f:
                f.write("{}")

        validOTPCodes = json.load(open('validOTPCodes.txt', 'r'))

        print("Prepping environment for analytics...please wait!")
        time.sleep(2)
        AccessAnalytics.prepEnvironmentForAnalytics()

        # Gather inputs
        print()

        identityUsername = input("Enter the username of the identity you would like to delete: ")
        while True:
            if identityUsername not in accessIdentities:
                print("No such identity has that username.")
                identityUsername = input("Enter the username of the identity you would like to delete: ")
                continue
            break
        
        targetIdentity = {}
        for username in accessIdentities:
            if username == identityUsername:
                targetIdentity = copy.deepcopy(accessIdentities[username])
                targetIdentity['username'] = username
        
        password = getpass("For security purposes, you will have to enter the identity's password: ")
        while True:
            if password != CertAuthority.decodeFromB64(targetIdentity['password']):
                print("Incorrect identity password. Try again.")
                password = getpass("For security purposes, you will have to enter the identity's password: ")
                continue
            break

        print()
        print("Processing identity deletion request...please wait!")
        print()
        time.sleep(2)
        
        # Delete identity from existence

        ## possible validOTPCode entries
        if targetIdentity['email'] in validOTPCodes:
            validOTPCodes.pop(targetIdentity['email'])

        ## Delete certificate
        response = CertAuthority.permanentlyDeleteCertificate(targetIdentity['associatedCertID'])
        if CAError.checkIfErrorMessage(response):
            print("DELETE IDENTITY DEVTOOL SYSTEMERROR: Error response received from CA when attempting to delete identity certificate: {}".format(response))
            print("Startup will now close.")
            sys.exit(1)
        elif response != "Successfully deleted that certificate.":
            print("DELETE IDENTITY DEVTOOL SYSTEMERROR: An unknown response string was received from CA when attempting to delete identity certificate: {}".format(response))
            print("Startup will now close.")
            sys.exit(1)
    
        ## Delete Access Folder
        if AFManager.checkIfFolderIsRegistered(targetIdentity['username']):
            afmResponse = AFManager.deleteFolder(targetIdentity['username'])
            if AFMError.checkIfErrorMessage(afmResponse):
                print("DELETE IDENTITY DEVTOOL SYSTEMERROR: Error response received from AFM when attempting to delete identity's Access Folder: {}".format(afmResponse))
                print("Startup will now close.")
                sys.exit(1)
    
        ## Delete identity records
        try:
            accessIdentities.pop(targetIdentity['username'])
        except Exception as e:
            print("DELETE IDENTITY DEVTOOL SYSTEMERROR: An error occurred in deleting identity records: {}".format(e))
            print("Startup will now close.")
            sys.exit(1)

        ## SAVE ALL CHANGES TO DATABASE
        try:
            json.dump(validOTPCodes, open('validOTPCodes.txt', 'w'))
        except Exception as e:
            print("DELETE IDENTITY DEVTOOL SYSTEMERROR: Failed to update OTP codes database with deletion of entries associated with the Access Identity; Error: {}".format(e))
            print("Startup will now close.")
            sys.exit(1)

        try:
            json.dump(accessIdentities, open('accessIdentities.txt', 'w'))
        except Exception as e:
            print("DELETE IDENTITY DEVTOOL SYSTEMERROR: Failed to update database with the deletion of the identity's records; Error: {}".format(e))
            print("Startup will now close.")
            sys.exit(1)

        try:
            savingDeletionCAResponse = CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))
            if CAError.checkIfErrorMessage(savingDeletionCAResponse):
                print("DELETE IDENTITY DEVTOOL SYSTEMERROR: Error response received from CA when attempting to save certificate deletion to database: {}".format(savingDeletionCAResponse))
                print("Startup will now close.")
                sys.exit(1)
        except Exception as e:
            print("DELETE IDENTITY DEVTOOL SYSTEMERROR: An error occurred when attempting to update database with the deletion of the identity's certificate; Error: {}".format(e))
            print("Startup will now close.")
            sys.exit(1)
    
        # Update Access Analytics
        aaResponse = AccessAnalytics.newIdentityDeletion()
    
        if isinstance(aaResponse, str):
            if aaResponse.startswith("AAError"):
                print("DELETE IDENTITY DEVTOOL: Failed to update Access Analytics with new identity deletion; Response: {}".format(aaResponse))
            else:
                print("DELETE IDENTITY DEVTOOL: Unknown string response received from Access Analytics when attempting to update with new identity deletion; Response: {}".format(aaResponse))
        elif aaResponse != True:
            print("DELETE IDENTITY DEVTOOL: Unknown response received from Access Analytics when attempting to update with new identity deletion; Response: {}".format(aaResponse))
        else:
            print("DELETE IDENTITY DEVTOOL: Updated Access Analytics with new identity deletion.")

        print()
        print("Identity was successfully wiped from system.")
    elif devToolsChoice == 3:
        print()
        print("Reading all identities' data from database files...")
        print()
        time.sleep(2)

        # Load access identities
        if not os.path.isfile('accessIdentities.txt'):
            with open('accessIdentities.txt', 'w') as f:
                f.write("{}")

        accessIdentities = json.load(open('accessIdentities.txt', 'r'))

        loopIndex = 1
        for username in accessIdentities:
            print("({})".format(loopIndex))
            print("\tUsername: {}".format(username))
            print("\tEmail: {}".format(accessIdentities[username]["email"]))
            print("\tPassword (Encrypted): {}".format(accessIdentities[username]["password"]))
            print("\tSign-Up Date: {}".format(accessIdentities[username]["sign-up-date"]))
            print("\tAssociated Sign-Up OTP Code: {}".format(accessIdentities[username]["otpCode"]))
            print("\tLast Login Date: {}".format(accessIdentities[username]["last-login-date"]))
            if "loggedInAuthToken" in accessIdentities[username]:
                print("\tSigned-In Status: True, Auth Token: {}".format(accessIdentities[username]["loggedInAuthToken"]))
            else:
                print("\tSigned-In Status: False")
            print("\tAssociated Certificate ID: {}".format(accessIdentities[username]["associatedCertID"]))
            if accessIdentities[username]["folderRegistered"] == True:
                print("\tAccess Folder: Registered")
                print("\t\tFiles:")
                if accessIdentities[username]["AF_and_files"] == {}:
                    print("\t\tNo files in folder.")
                else:
                    print("\t\tNAME\t\t\t\tUPLOAD DATE")
                    for file in accessIdentities[username]["AF_and_files"]:
                        print("\t\t{}\t\t{}".format(file, accessIdentities[username]["AF_and_files"][file]))
            else:
                print("\tAccess Folder: Not Registered")
            print("\tSettings:")
            for preference in accessIdentities[username]["settings"]:
                print("\t\t{}: {}".format(preference, accessIdentities[username]["settings"][preference]))

            print()
            print()
            loopIndex += 1
        
        print("-----")
        print("END OF IDENTITIES' DATA")
        print()
    elif devToolsChoice == 4:
        print()
        print("Initializing Cert Editing Tools...")
        print()
        time.sleep(2)

        # Load certificates
        if not os.path.isfile('certificates.txt'):
            with open('certificates.txt', 'w') as f:
                f_content = """{ "registeredCertificates": {}, "revokedCertificates": {}}"""
                f.write(f_content)

        CAresponse = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
        if CAError.checkIfErrorMessage(CAresponse):
            print("CERT EDIT DEV TOOL: Error in loading certificates; response from CA: " + CAresponse)
            sys.exit(1)
        print()


        print("""
Welcome to Certificate Editing Tools! This tool is designed to allow you to edit the certificates that are stored in the CA.
    
Please choose an option from below:
        
    1) View all certificates
    2) Create a certificate
    3) Revoke a certificate
    4) Delete a certificate
    5) Re-hash a certificate
        
        """)

        certEditToolsChoice = int(input("Enter your choice: "))
        print()

        if certEditToolsChoice == 1:
            # View all certificates
            print("Reading all certificates' data...")
            time.sleep(2)
            print()

            regCerts = CertAuthority.registeredCertificates
            revokedCerts = CertAuthority.revokedCertificates

            print("REGISTERED CERTIFICATES:")
            print("------------------------")
            print()

            if regCerts == {}:
                print("No registered certificates.")
            else:
                loopIndex = 1
                for username in regCerts:
                    print("({})".format(loopIndex))
                    print("\tUsername of Identity Attached to Certificate: {}".format(username))
                    print("\tCertificate ID: {}".format(regCerts[username]["certID"]))
                    print("\tResponse From CertAuthority About Certificate's Security: {}".format(CertAuthority.checkCertificateSecurity(regCerts[username])))
                    print("\tExpiry Date: {}".format(regCerts[username]["expiryDate"]))
                    if regCerts[username]["revoked"] == True:
                        print("\tRevoked: True, Reason: {}".format(regCerts[username]["revocationReason"]))
                    else:
                        print("\tRevoked: False")
                    print("\tIssue Date: {}".format(regCerts[username]["issueDate"]))
                    print()

                    loopIndex += 1

            print()
            print("REVOKED CERTIFICATES:")
            print("---------------------")

            if revokedCerts == {}:
                print("No revoked certificates.")
            else:
                loopIndex = 1
                for username in revokedCerts:
                    print("({})".format(loopIndex))
                    print("\tUsername of Identity Attached to Certificate: {}".format(username))
                    print("\tCertificate ID: {}".format(revokedCerts[username]["certID"]))
                    print("\tResponse From CertAuthority About Certificate's Security: {}".format(CertAuthority.checkCertificateSecurity(revokedCerts[username])))
                    print("\tExpiry Date: {}".format(revokedCerts[username]["expiryDate"]))
                    if revokedCerts[username]["revoked"] == True:
                        print("\tRevoked: True, Reason: {}".format(revokedCerts[username]["revocationReason"]))
                    else:
                        print("\tRevoked: False")
                    print("\tIssue Date: {}".format(revokedCerts[username]["issueDate"]))
                    print()

                    loopIndex += 1

            print()
            print("-----------------")
            print("End of certificates data.")
            print()
        elif certEditToolsChoice == 2:
            pass

            


