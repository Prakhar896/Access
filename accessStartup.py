import time, os, shutil
from getpass import getpass
from accessAnalytics import *

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
        import main
        main.boot()

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
        5) Manage Logs
        6) Factory Reset - Delete System and User Information Data Files, Access Folders, Analytics Reports
""")
    
        while True:
            try:
                choice = int(input("Enter your choice: "))
                if choice not in range(0, 7): raise Exception()
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
            ## Manage Logs
            print("STARTUP: Activating log management...")
            print()
            Logger.manageLogs()
            print()
        elif choice == 6:
            ## Delete data files
            print()
            print("STARTUP: Please wait a while for Startup to delete all data files...")
            print()
            time.sleep(2)

            raise Exception("Factory Reset is disabled for now.")

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