# Set DeveloperModeEnabled to "True" in .env file to enable the Developer Tools Suite
import time, json, os, datetime
from models import systemWideStringDateFormat
from getpass import getpass
from certAuthority import *
def toolsStartup():

    print("""
Welcome to the Developer Tools Suite!
(PRO Tip: This suite is displayed because you have enabled Developer Mode
by setting "DeveloperModeEnabled" to "True" in the .env file.)

Options:

        1) Create a new Identity
        2) Delete an Identity
        3) Cert Authority and Certificates Tools

    """)
    devToolsChoice = int(input("What would you like to do: "))
    print()
    if devToolsChoice == 1:
        # Initiate manual Create identity process; ask user for parameter inputs
        print("Initiating Manual Create Identity Process...Please give inputs as follows...")
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
        return