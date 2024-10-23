import os, sys, time, datetime, shutil, platform, requests
from dotenv import load_dotenv
load_dotenv()

print("Welcome to Access CheckUp!")
print("This sub-service will check the Access environment for irregularities that may need to be fixed for improved system functionality.")
print()
print("Please wait a while while CheckUp scans the system environment (this may take some time)...")
print()

time.sleep(2)

if os.path.isfile(os.path.join(os.getcwd(), 'requirements.txt')):
    print("Would you like to install/re-install all libraries from the 'requirements.txt' file?")
    action = input("Type 'yes' or 'no': ")
    if action == "yes":
        print()
        print("Re-installing...")
        os.system("pip install -r requirements.txt")
        print()
        print("CheckUp successfully installed the libraries. Proceeding with normal procedures...")
        print()
    elif action == "no":
        print("Proceeding with normal procedures...")
        print()
    else:
        print("Invalid action provided. CheckUp will proceed with normal procedures...")
        print()

critical_issues = []
warnings = []

print("CheckUp procedures will start now...")
print()


# Coming soon