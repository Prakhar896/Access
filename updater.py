import os, shutil, sys, json, time, requests, subprocess
from models import Universal

# Check for updates
print("Checking for updates...")
print()

def is_git_installed():
    try:
        subprocess.check_output(["git", "--version"])
        return True
    except Exception:
        return False

if not is_git_installed():
    print("Git is not installed or not in the system's PATH. Updater requires a Git installation; please install Git and try again.")
    sys.exit(1)

# Get current version number
currentVersion = Universal.getVersion()
if currentVersion == "Version File Not Found":
    print("No version.txt file was found at the root of the system folder. Failed to check for updates.")
    sys.exit(1)

# Get latest RC number
mesuResponse = requests.get("https://prakhar896.github.io/meta/access/latestVersion.html")
try:
    mesuResponse.raise_for_status()
except Exception as e:
    print("Failed to check for updates; error: {}".format(e))
    sys.exit(1)
latestVersion = mesuResponse.text[len("<p>"):len(mesuResponse.text)-len("</p>")]

targetedVersion = None
if latestVersion == currentVersion:
    print("Access is up to date!")
    print()
    switch = input("Would you still like to switch to another version? (y/n) ")
    if switch.lower() == 'y':
        targetedVersion = input("Enter target version number (with 'v' preceding it): ")
    else:
        sys.exit(1)
else:
    print("Newer update found! The latest version is 'v{}'.".format(latestVersion))
    targetChoice = input("Would you like to update to this version or another version? (this/other): ")
    if targetChoice.lower() == 'this':
        targetedVersion = 'v' + latestVersion
    elif targetChoice.lower() == 'other':
        targetedVersion = input("Enter target version number (with 'v' preceding it): ")
    else:
        print("Invalid option provided. Aborting...")
        sys.exit(1)

print()
print("Beginning update procedure...")

ghUsername = "Prakhar896" # input("Enter the github username: ")
ghRepo = "Access" # input("Enter the github repository: ")

print()
print("Deleting all irrelevant files...")

# Delete all files and folders in the current directory
dataFilesList = [
    'analyticsData.txt', 
    'certificates.txt', 
    'accessIdentities.txt', 
    'validOTPCodes.txt', 
    '.env', 
    'authorisation.txt', 
    'licensekey.txt',
    'config.txt'
]
# Delete all files and folders in the current directory
for root, dirs, files in os.walk(os.getcwd(), topdown=False):
    for name in files:
        if name != "updater.py" and (name not in dataFilesList) and (not name.startswith('aa-report')) and ("AccessFolders" not in root) and ('venv' not in root) and ('virt' not in root):
            os.remove(os.path.join(root, name))
    for name in dirs:
        if (name not in ["analyticsReports", "AccessFolders"]) and ("AccessFolders" not in root) and (name not in ['venv', 'virt']) and ('virt' not in root) and ('venv' not in root):
            shutil.rmtree(os.path.join(root, name))

time.sleep(2)

# Clone the repository
print()
print("Cloning the repository...")
print()
os.system("git clone https://github.com/" + ghUsername + "/" + ghRepo)
time.sleep(2)
print()
print("Moving files...")
print()
# Move the files and folders to the current directory
for root, dirs, files in os.walk(os.path.join(os.getcwd(), ghRepo)):
    try:
        for name in files:
            if name != 'updater.py':
                shutil.move(os.path.join(os.getcwd(), ghRepo, name), os.getcwd())
        for name in dirs:
            if os.path.isdir(os.path.join(os.getcwd(), ghRepo, name)):
                shutil.move(os.path.join(os.getcwd(), ghRepo, name), os.getcwd())
    except Exception as e:
        print("Error moving files and folders:", e)

time.sleep(2)

# Delete the repository folder
print("Deleting the repository folder...")
print()
shutil.rmtree(os.path.join(os.getcwd(), ghRepo))
time.sleep(2)

# Show sucesss
print("Successfully updated to latest commit of the repository!")

print()
print("Attempting to switch to targeted version...")
time.sleep(2)
print()
print("----- GIT VERSION SWITCHING OUTPUT")
try:
    os.system("git checkout " + targetedVersion)
    print("------ END OF GIT OUTPUT")
    print()
    print("Switched to version successfully! (If the above output does not show a successful switch, you will have to manually use the 'git checkout <version tag>' command)")
except Exception as e:
    print("Error in switching to target version:", e)
    print("To use the version you want, use the comamand 'git checkout <version tag, for e.g v1.0>")

print()
print("Updating Updater service itself...")
print()
time.sleep(2)

print("----- GIT OUTPUT FOR UPDATING UPDATER SERVICE")
os.system("git checkout updater.py")
print("------ END OF GIT OUTPUT")

print()
print("Finished updating operations!")