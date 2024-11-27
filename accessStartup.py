import time, os, shutil
from getpass import getpass
from AFManager import AFManager
from services import Logger
from accessAnalytics import *

print("Welcome to Access Startup!")
print("Here you can manage and run all things Access.")

while True:
    print("""
Startup Choices - What would you like to do?

    1) Access Boot
    2) Access Analytics - Crunch Data and Report
    3) General Settings
    4) Update Access
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
        print("STARTUP: Running Access Analytics crunch data function...")
        print()
        AccessAnalytics.crunchData()
        print()
        print("STARTUP: Access Analytics crunch data function has finished running.")
    elif choice == 3:
        import config
        startupConfigManager = config.Config()
        
        print("""
General Settings: (0 to return to main menu)
        
        1) Configure allowed file extensions
        2) Configure maximum directory size
        3) Configure maximum file count
        4) Configure maximum request length
        5) Access Analytics - Clear Collected Data
        6) Access Analytics Recovery Mode
        7) Manage Logs
        8) Factory Reset - Reset database, delete user directories, clear analytics reports
""")
    
        while True:
            try:
                choice = int(input("Enter your choice: "))
                if choice not in range(0, 9): raise Exception()
                break
            except:
                print("Invalid choice provided.")
                continue
    
        print()
        if choice == 1:
            config.manageFileExtensions(configManager=startupConfigManager)
            startupConfigManager.reload()
        elif choice == 2:
            config.manageDirectorySize(configManager=startupConfigManager)
            startupConfigManager.reload()
        elif choice == 3:
            config.manageFileCount(configManager=startupConfigManager)
            startupConfigManager.reload()
        elif choice == 4:
            config.manageRequestSize(configManager=startupConfigManager)
            startupConfigManager.reload()
        elif choice == 5:
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
        elif choice == 6:
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
        elif choice == 7:
            ## Manage Logs
            print("STARTUP: Activating log management...")
            print()
            Logger.manageLogs()
            print()
        elif choice == 8:
            ## Delete data files
            print()
            print("STARTUP: Resetting...")
            print()
            time.sleep(2)

            from database import DI
            res = DI.setup()
            if res != True:
                print("STARTUP: Error in resetting database; response: {}".format(res))
                sys.exit(1)
            
            DI.save(None)
            print("STARTUP DI: Database reset.")
            
            try:
                shutil.rmtree(AFManager.rootDirPath(), ignore_errors=True)
                print("STARTUP: Deleted user directories.")
            except Exception as e:
                print("STARTUP: Error in deleting user directories; Error: {}".format(e))
                sys.exit(1)
            
            AccessAnalytics.clearDataFile()
            if os.path.isdir(os.path.join(os.getcwd(), "analyticsReports")):
                try:
                    shutil.rmtree(os.path.join(os.getcwd(), "analyticsReports"), ignore_errors=True)
                    print("STARTUP: Deleted analytics reports and data.")
                except Exception as e:
                    print("STARTUP: Error in deleting analytics reports directory; Error: {}".format(e))
                    sys.exit(1)
            
            if os.path.isfile(os.path.join(os.getcwd(), "config.json")):
                try:
                    os.remove(os.path.join(os.getcwd(), "config.json"))
                    print("STARTUP: Deleted config file.")
                except Exception as e:
                    print("STARTUP: Error in deleting config file; Error: {}".format(e))
                    sys.exit(1)
            
            print()
            print("STARTUP: Factory reset complete.")
    elif choice == 4:
        import updater
        print("STARTUP: Startup will now close.")
        sys.exit(0)