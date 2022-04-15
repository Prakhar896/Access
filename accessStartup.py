import time, os, shutil
from getpass import getpass
from certAuthority import *

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    print("Startup Dotenv Library Loading Error: {}".format(e))
    print("Failed to import dotenv library to load environment variables. Attempting to install libraries from requirements.txt...")
    time.sleep(2)

    if not os.path.isfile(os.path.join(os.getcwd(), 'requirements.txt')):
        print()
        print("No requirements.txt file was found. Startup cannot startup.")
        sys.exit(1)
    else:
        os.system("pip install -r requirements.txt")
        print()
        print("Startup: Successfully downloaded libraries...re-importing dotenv...")
        print()
        from dotenv import load_dotenv
        load_dotenv()
        print()
        print("Successfully imported! Starting now...")
        print()

from accessAnalytics import *

print("Welcome to Access Startup!")
print()
print("Here you can manage and run all things Access!")
print()
print()
print("""
Startup Choices - What would you like to do?

    1) Access Boot
    2) Access Meta Settings
    3) Access CheckUp
    4) Access Analytics - Crunch Data
    5) System Update Guide


""")

while True:
    try:
        choice = int(input("Enter your choice number: "))
        break
    except:
        print("Invalid choice provided.")
        continue

if choice == 1:
    ## Begin Access Boot
    from main import *
    if __name__ == "__main__":
        # Boot Authorisation
        if os.path.isfile(os.path.join(os.getcwd(), 'authorisation.txt')):
            try:
                with open('authorisation.txt', 'r') as f:
                    decoded = CertAuthority.decodeFromB64(f.read())
                    code = getpass("MAIN: Enter your Boot Authorisation Code to begin Access Boot: ")
                    if code != decoded:
                        print("MAIN: Boot Authorisation Code is incorrect. Main will not proceed with the boot.")
                        sys.exit(1)
                    else:
                        print()
            except Exception as e:
                print("MAIN: Failed to load and ask for boot authorisation code. Error: {}".format(e))
                print("MAIN: Main will not proceed with the boot.")
                sys.exit(1)

    # Load certificates
    CAresponse = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
    if CAError.checkIfErrorMessage(CAresponse):
        print(CAresponse)
        sys.exit(1)
    else:
        print(CAresponse)
  
    # Expire old certificates and save new data
    CertAuthority.expireOldCertificates()
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))

    ## Expire auth tokens
    tempIdentities = accessIdentities
    accessIdentities = expireAuthTokens(tempIdentities)
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

    ## Set up Access Analytics
    if AccessAnalytics.permissionCheck():
        AAresponse = AccessAnalytics.prepEnvironmentForAnalytics()
        if AAresponse.startswith("AAError:"):
            print("MAIN: Error in getting Analytics to prep environment. Response: {}".format(AAresponse))
            print()
            print("MAIN: Would you like to enable Analytics Recovery Mode?")
            recoveryModeAction = input("Type 'yes' or 'no': ")
            if recoveryModeAction == "yes":
                AccessAnalytics.analyticsRecoveryMode()
            elif recoveryModeAction == "no":
                print("MAIN: Recovery mode was not enabled. Access Boot is aborted.")
                sys.exit(1)
            else:
                print("MAIN: Invalid action provided. Access Boot is aborted.")
                sys.exit(1)
        elif AAresponse != "AA: Environment prep successful.":
            print("MAIN: Unknown response when attempting to get Analytics to prep environment. Response: {}".format(AAresponse))
            print()
            print("MAIN: Would you like to enable Analytics Recovery Mode?")
            recoveryModeActionTwo = input("Type 'yes' or 'no': ")
            if recoveryModeActionTwo == "yes":
                AccessAnalytics.analyticsRecoveryMode()
            elif recoveryModeActionTwo == "no":
                print("MAIN: Recovery mode was not enabled. Access Boot is aborted.")
                sys.exit(1)
            else:
                print("MAIN: Invalid action provided. Access Boot is aborted.")
                sys.exit(1)
        else:
            print(AAresponse)
    else:
        print("MAIN: Notice!!! AccessAnalytics is not enabled and will not be setup and run.")

    ## Port check
    if 'RuntimePort' not in os.environ:
        print("MAIN: RuntimePort environment variable is not set in .env file. Access cannot be booted without a valid port set. Please re-boot Access after setting RuntimePort.")
        sys.exit(1)
    elif not os.environ['RuntimePort'].isdigit():
        print("MAIN: RuntimePort environment variable has an invalid value. Port value must be an integer.")
        sys.exit(1)
      
    print("All services are online; boot pre-processing and setup completed.")
    print()
    print("Booting Access...")
    print()
    app.run(host='0.0.0.0', port=int(os.environ['RuntimePort']))

    
    print()
    print("STARTUP: Access Startup will now close.")
elif choice == 2:
    # Meta Settings - Make authorisation code, Run Access Analytics Recovery Mode
    print()
    print("Meta Settings:")
    print()
    print("""
    Choices:

        1) Access Analytics - Clear Collected Data
        2) Access Analytics - Recovery Mode
        3) Factory Reset - Delete System and User Information Data Files, Access Folders, Analytics Reports
        4) Manage Boot Authorisation Code

    """)

    while True:
        try:
            metaChoice = int(input("Enter your choice number: "))
            break
        except Exception as e:
            print("Invalid choice provided. Please try again.")
            continue
        
    if metaChoice == 1:
        ## Clear collected data
        print()
        print("STARTUP: Executing Access Analytics Clear Data Script...")
        print()
        time.sleep(2)
        response = AccessAnalytics.clearDataFile()
        if isinstance(response, str):
            if response.startswith("AAError:"):
                print("STARTUP: Error in clearing analytics data file; Response: {}".format(response))
                sys.exit(1)
            else:
                print("STARTUP: Unknown response receieved from AA when trying to clear data file; Response: {}".format(response))
                sys.exit(1)
        elif response != True:
            print("STARTUP: Unknown response received from AA; Response: {}".format(response))
            sys.exit(1)
        print()
        print("STARTUP: Successfully cleared analytics data file.")
        print("STARTUP: Access Startup will now close.")
    elif metaChoice == 2:
        ## Analytics Recovery mode
        print()
        print("STARTUP: Initialising Access Analytics Recovery Mode...")
        print()
        time.sleep(2)
        try:
            AccessAnalytics.analyticsRecoveryMode()
        except Exception as e:
            print()
            print("STARTUP: An error occurred in recovery mode; Error: {}".format(e))
            sys.exit(1)
        print()
        print("STARTUP: Access Startup will now close.")
        sys.exit(0)
    elif metaChoice == 3:
        ## Delete data files
        print()
        print("STARTUP: Please wait a while for Startup to delete all data files...")
        print()
        time.sleep(3)

        dataFilenames = [
            'accessIdentities.txt',
            'analyticsData.txt',
            'certificates.txt',
            'validOTPCodes.txt'
        ]

        errorsPresent = False

        for filename in dataFilenames:
            if os.path.isfile(os.path.join(os.getcwd(), filename)):
                try:
                    os.remove(os.path.join(os.getcwd(), filename))
                except Exception as e:
                    print("STARTUP: There was an error in deleting the file {}; Error: {}".format(filename, e))
                    errorsPresent = True

        ## Delete AccessFolders
        if os.path.isdir(os.path.join(os.getcwd(), 'AccessFolders')):
            try:
                shutil.rmtree('AccessFolders')
            except Exception as e:
                print("STARTUP: There was an error in deleting the AccessFolders directory; Error: {}".format(e))
                errorsPresent = True
        
        ## Delete Analytics Reports
        if os.path.isdir(os.path.join(os.getcwd(), 'analyticsReports')):
            try:
                shutil.rmtree('analyticsReports')
            except Exception as e:
                print("STARTUP: There was an error in deleting the analyticsReports directory; Error: {}".format(e))
                errorsPresent = True
        
        print()
        if errorsPresent:
            print("STARTUP: Startup deleted everything but there were some errors in deleting some of the files. See the errors above for more information. Startup will now close.")
            sys.exit(1)
        print("STARTUP: Successfully deleted all files, Access Folders and stored Access Analytics reports. Startup will now close.")
        sys.exit(0)
    elif metaChoice == 4:
        ## Manage Boot Authorisation Code
        if not os.path.isfile('authorisation.txt'):
            ## Make new code
            print()
            print("Startup has detected that you have no Boot Authorisation code set yet.")
            print()
            print("Q. What is a boot authorisation code?")
            print("Ans: A boot authorisation code will secure your Access Boot process by preventing anyone other than the owner of the system from booting to system. Before the system is booted, if set, it will ask you for your boot authorisation code which is required to procede with the boot. A wrong code will interrupt and terminate the boot process.")
            print()
            wouldLikeToSet = input("Would you like to set a boot authorisation code? (y/n) ")
            while wouldLikeToSet not in ['y', 'n']:
                print("Invalid action provided. Please try again.")
                wouldLikeToSet = input("Would you like to set a boot authorisation code? (y/n) ")
            
            if wouldLikeToSet == "y":
                print()
                code = getpass("Enter a booth authorisation code of your choice: ")
                print()
                print("Setting code...")
                print()
                time.sleep(2)
                try:
                    with open('authorisation.txt', 'w') as f:
                        f.write(CertAuthority.encodeToB64(code))
                except Exception as e:
                    print("STARTUP: An error occurred in setting the code; Error: {}".format(e))
                    sys.exit(1)
                print("Code set successfully. Access Startup will now close.")
                sys.exit(0)
            else:
                print()
                print("Set process aborted. Access Startup will now close.")
                sys.exit(0)
        else:
            ## Authorisation code is already set
            print()
            print("Startup has detected that an authorisation code is already set.")
            print()
            print("""
            What would you like to do:
                
                1) Remove boot authorisation code
                2) Change code

            """)
            print()
            while True:
                try:
                    alreadySetChoice = int(input("Enter your choice: "))
                    break
                except Exception as e:
                    print("Invalid choice number. Please try again.")
                    continue
            print()
            if alreadySetChoice == 1:
                while True:
                    checkCode = getpass("Enter your current boot authorisation code: ")

                    with open('authorisation.txt', 'r') as f:
                        if checkCode == CertAuthority.decodeFromB64(f.read()):
                            break
                        else:
                            print("Invalid code. Please try again.")
                            continue
                    
                print()
                print("Removing boot authorisation code...")
                time.sleep(2)

                try:
                    os.remove(os.path.join(os.getcwd(), 'authorisation.txt'))
                except Exception as e:
                    print()
                    print("An error occurred in removing the code; Error: {}".format(e))
                    sys.exit(1)
                    
                print()
                print("STARTUP: Removed boot authorisation code successfully. Access Startup will now close.")
                sys.exit(0)
            elif alreadySetChoice == 2:
                print()
                while True:
                    checkCode = getpass("Enter your current boot authorisation code: ")

                    with open('authorisation.txt', 'r') as f:
                        if checkCode == CertAuthority.decodeFromB64(f.read()):
                            break
                        else:
                            print("Invalid code. Please try again.")
                            continue
                
                newCode = getpass("Enter your new boot authorisation code: ")
                print()
                print("Updating code...")
                time.sleep(2)

                try:
                    with open('authorisation.txt', 'w') as f:
                        f.write(CertAuthority.encodeToB64(newCode))
                except Exception as e:
                    print("An error occurred in updating the code; Error: {}".format(e))
                    sys.exit(1)
                print()
                print("Successfully updated boot authorisation code. Access Startup will now close.")
                sys.exit(0)
elif choice == 3:
    # Run Access CheckUp
    print()
    print("Startup: Initialising Access CheckUp service...")
    print()
    print()
    import accessCheckup
    print()
    print("Startup: Exiting startup...")
elif choice == 4:
    ## Run Crunch Data in Access Analytics
    print("Running data analysis function...")
    print()
    print()
    AccessAnalytics.crunchData()
    print()
    print("STARTUP: Access Startup will now close.")
elif choice == 5:
    print("""

Welcome to the Access Startup Update Guide! This guide will walk you through on how you can manually update the system. There are three main steps to the update procedure:

    1) Move data files and folders out into a temporary folder

        If any of the following files/folders are present in your current system folder, move them out to any temporary folder on your system:
            - AccessFolders (folder)
            - analyticsReports (folder)
            - .env (file)
            - accessIdentities.txt (file)
            - analyticsData.txt (file)
            - authorisation.txt (file)
            - certificates.txt (file)
            - validOTPCodes.txt (file)
    
    2) Obtain a copy of the latest version of Access

        First, go to the GitHub Repository (https://github.com/Prakhar896/Access) and click on the latest version release under the "Releases" section on the right.
        The version number should be higher than the current system version you have which is "{}" 
        Remember this version number, you will need it later.

        If you would like to get a new and fresh copy of Access, run "git clone https://github.com/Prakhar896/Access" in your command line in the directory
        where you want to place the system.
        Then, you will have to run the command "git checkout <VERSION NUMBER HERE>" where you replace <VERSION NUMBER HERE> with the version you saw earlier.

        If not, when you first got this system, a git repository folder came with it so you can actually pull the new changes via the command line command "git pull".
        Then, you will have to run the command "git checkout v<VERSION NUMBER HERE>" where you replace <VERSION NUMBER HERE> with the version you saw earlier.
        For example, "git checkout v1.0".
    
    3) Move data files and folders back to the system folder

        This step is pretty simple. Simply move all the folders and files you moved out earlier back into the new updated system's folder and run Access CheckUp to ensure
        that everything is alright. Then boot up Access and you are good to go with a freshly updated system!
    
    That is the end of this user guide.
    Startup will now close.
    """.format(open('version.txt', 'r').read()))
