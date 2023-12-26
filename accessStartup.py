import time, os, shutil
from getpass import getpass
import pkg_resources

try:
    required = {'flask', 'flask-cors', 'passlib', 'getmac', 'python-dotenv'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed
    if missing:
        raise Exception("Missing Libraries: " + ', '.join([x for x in missing]))
except Exception as e:
    print("Startup Library Loading Error: {}".format(e))
    print("Failed to import one or more libraries. Attempting to install libraries from requirements.txt...")
    time.sleep(2)

    if not os.path.isfile(os.path.join(os.getcwd(), 'requirements.txt')):
        print()
        print("No requirements.txt file was found. Startup cannot startup.")
        sys.exit(1)
    else:
        os.system("pip install -r requirements.txt")
        print()
        print("Startup: Successfully downloaded libraries! Re-importing...")
        print()
        from dotenv import load_dotenv
        load_dotenv()
        print("Successfully imported! Starting now...")
        print()

from accessAnalytics import *
from certAuthority import *

if 'FileUploadsLimit' not in os.environ:
    print("STARTUP WARNING: Mandatory `FileUploadsLimit` environment variable is not set in .env file. The system will fall back on the default limit of '3' file uploads when booted.")
    print()


print("Welcome to Access Startup!")
print("Here you can manage and run all things Access.")

while True:
    print("""
Startup Choices - What would you like to do?

    1) Access Boot
    2) Access CheckUp
    3) Access Analytics - Crunch Data and Report
    4) General Settings
    5) Update Access
""")

    while True:
        try:
            choice = int(input("Enter your choice number: "))
            break
        except:
            print("Invalid choice provided.")
            continue
    
    print()
    if choice == 0:
        print("Bye!")
        sys.exit(0)
    elif choice == 1:
        ## Begin Access Boot
        from main import *
        if __name__ == "__main__":
            bootFunction()

        print()
        print("STARTUP: Access Startup will now close.")
        sys.exit(0)
    elif choice == 2:
        print("STARTUP: Running Access CheckUp service...")
        print()
        import accessCheckup
        print()
        print("STARTUP: Access CheckUp service has finished running.")
    elif choice == 3:
        print("STARTUP: Running Access Analytics crunch data function...")
        print()
        AccessAnalytics.crunchData()
        print()
        print("STARTUP: Access Analytics crunch data function has finished running.")
    elif choice == 4:
        import config
        startupConfigManager = config.Config()
        
        print("""
General Settings: (0 to return to main menu)
        
        1) Configure allowed file extensions
        2) Configure allowed file size
        3) Access Analytics - Clear Collected Data
        4) Access Analytics Recovery Mode
        5) Manage Boot Authorisation Code
        6) Manage Logs
        7) Factory Reset - Delete System and User Information Data Files, Access Folders, Analytics Reports
""")
    
        while True:
            try:
                choice = int(input("Enter your choice: "))
                if choice not in range(0, 8): raise Exception()
                break
            except:
                print("Invalid choice provided.")
                continue
    
        print()
        if choice == 1:
            config.manageFileExtensions(configManager=startupConfigManager)
            startupConfigManager.reload()
        elif choice == 2:
            config.manageFileSize(configManager=startupConfigManager)
            startupConfigManager.reload()
        elif choice == 3:
            ## Clear collected data
            print()
            print("STARTUP: Clearing Access Analytics collected data...")
            print()
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
        elif choice == 4:
            ## Analytics Recovery mode
            print()
            print("STARTUP: Initialising Access Analytics Recovery Mode...")
            print()
            try:
                AccessAnalytics.analyticsRecoveryMode()
            except Exception as e:
                print()
                print("STARTUP: An error occurred in recovery mode; Error: {}".format(e))
                sys.exit(1)
            print()
        elif choice == 5:
            ## Manage Boot Authorisation Code
            if not os.path.isfile(os.path.join(os.getcwd(), 'authorisation.txt')):
                ## Make new code
                print()
                print("Startup has detected that you have no Boot Authorisation code set yet.")
                print()
                print("A boot authorisation code will secure your Access Boot process by preventing anyone other than the owner of the system from booting the system. Before the system is booted, if set, it will ask you for your boot authorisation code which is required to procede with the boot. A wrong code will interrupt and terminate the boot process.")
                print()
                wouldLikeToSet = input("Would you like to set a boot authorisation code? (y/n) ")
                while wouldLikeToSet not in ['y', 'n']:
                    print("Invalid action provided. Please try again.")
                    wouldLikeToSet = input("Would you like to set a boot authorisation code? (y/n) ")
            
                if wouldLikeToSet == "y":
                    print()
                    code = getpass("Enter a boot authorisation code of your choice: ")
                    print()
                    print("Setting code...")
                    print()
                    try:
                        with open('authorisation.txt', 'w') as f:
                            f.write(Encryption.encodeToB64(code))
                    except Exception as e:
                        print("STARTUP: An error occurred in setting the code; Error: {}".format(e))
                        sys.exit(1)
                    print("Code set successfully.")
                else:
                    print()
                    print("Set process aborted.")
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
                        if alreadySetChoice not in range(0, 3):
                            raise Exception()
                        break
                    except Exception as e:
                        print("Invalid choice number. Please try again.")
                        continue
                print()

                if alreadySetChoice != 0:
                    ## Authorise user
                    while True:
                        checkCode = getpass("Enter your current boot authorisation code: ")

                        with open('authorisation.txt', 'r') as f:
                            if checkCode == Encryption.decodeFromB64(f.read()):
                                break
                            else:
                                print("Invalid code. Please try again.")
                                continue

                if alreadySetChoice == 1:
                    print()
                    print("Removing boot authorisation code...")

                    try:
                        os.remove(os.path.join(os.getcwd(), 'authorisation.txt'))
                    except Exception as e:
                        print()
                        print("An error occurred in removing the code; Error: {}".format(e))
                        sys.exit(1)
                    
                    print()
                    print("STARTUP: Removed boot authorisation code successfully.")
                elif alreadySetChoice == 2:
                    newCode = getpass("Enter your new boot authorisation code: ")
                    print()
                    print("Updating code...")

                    try:
                        with open('authorisation.txt', 'w') as f:
                            f.write(Encryption.encodeToB64(newCode))
                    except Exception as e:
                        print("An error occurred in updating the code; Error: {}".format(e))
                        sys.exit(1)
                    print()
                    print("Successfully updated boot authorisation code.")
        elif choice == 6:
            ## Manage Logs
            print("STARTUP: Activating log management...")
            print()
            Logger.manageLogs()
            print()
        elif choice == 7:
            ## Authorise user
            if os.path.isfile(os.path.join(os.getcwd(), "authorisation.txt")):
                while True:
                    checkCode = getpass("Enter your current boot authorisation code: ")

                    with open('authorisation.txt', 'r') as f:
                        if checkCode == Encryption.decodeFromB64(f.read()):
                            break
                        else:
                            print("Invalid code. Please try again.")
                            continue

            ## Delete data files
            print()
            print("STARTUP: Please wait a while for Startup to delete all data files...")
            print()
            time.sleep(2)

            dataFilenames = [
                'accessIdentities.txt',
                'analyticsData.txt',
                'certificates.txt',
                'validOTPCodes.txt',
                'authorisation.txt',
                'config.txt'
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
                print("STARTUP: There were some errors in deleting some of the files. See above. Startup will now close to force a context update.")
                sys.exit(1)
            print("STARTUP: Successfully deleted all files, Access Folders and stored Access Analytics reports. Startup will now close to force a context update.")
            sys.exit(0)
    elif choice == 5:
        import updater
        print("STARTUP: Startup will now close.")
        sys.exit(0)