import time, os, shutil
from getpass import getpass
from certAuthority import *
import pkg_resources

try:
    required = {'flask', 'flask-cors'}
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
        print("Startup: Successfully downloaded libraries...re-importing dotenv...")
        print()
        from dotenv import load_dotenv
        load_dotenv()
        print()
        print("Successfully imported! Starting now...")
        print()

from accessAnalytics import *

if 'FileUploadsLimit' not in os.environ:
    print("STARTUP WARNING: Mandatory `FileUploadsLimit` environment variable is not set in .env file. The system will fall back on the default limit of `3` file uploads when booted.")
    print()

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
        bootFunction()

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
            'validOTPCodes.txt',
            'authorisation.txt'
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
                code = getpass("Enter a boot authorisation code of your choice: ")
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
    
    Welcome to the Access System update guide! Updating Access is easy peasy with the built-in Access Updater service (aka the 'updater.py' file).

    Before running the file, you will need to know the latest Access Version Number. Do this by running Access CheckUp; if your system is truly out-of-date,
    you should see a critical issue pop up in the CheckUp summary report. The report should have the latest version number in it. Remember this, you will need it.

    Next, simply run the 'updater.py' python script using your command line with Python3, type 'y' (for yes), then type in the version number with the letter 'v' preceding it,
    like so: 'v1.0' (if the number is 1.0).

    Then, you should see Updater do its thing while it clears all old files, brings in the new files, switches to the targeted version of Access, and all the while keeps essential data
    files in the system, so that you do not lose any previously recorded data.

    And that's it! Simple, right!
    
    That is the end of this user guide.
    Startup will now close.
    """.format(open('version.txt', 'r').read()))
