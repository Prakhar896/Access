import os, shutil, sys, json, time

check = input("Are you very sure that you would like to update? This service will destroy all current non-data files and bring in the new data files, thus retaining data. (y/n): ")
if check != 'y':
    print("Exiting...")
    sys.exit(1)

targetedVersion = input("What is your target Access Version Number (for e.g, '1.0'): ")

ghUsername = "Prakhar896" # input("Enter the github username: ")
ghRepo = "Access" # input("Enter the github repository: ")

print()
print("Deleting all irrelevant files...")

# Delete all files and folders in the current directory
for root, dirs, files in os.walk(os.getcwd(), topdown=False):
    for name in files:
        if name != "updater.py" and (name not in ['analyticsData.txt', 'certificates.txt', 'accessIdentities.txt', 'validOTPCodes.txt', '.env']) and (not name.startswith('aa-report')):
            os.remove(os.path.join(root, name))
    for name in dirs:
        if name != 'analyticsReports' and name != 'AccessFolders':
            os.rmdir(os.path.join(root, name))

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
print()
print("Deleting the repository folder...")
print()
shutil.rmtree(os.path.join(os.getcwd(), ghRepo))
time.sleep(2)
print()

# Show sucesss
print("\nSuccessfully updated to latest commit of repository!")

print()
print("Attempting to switch to targeted version...")
time.sleep(2)
print()
try:
    os.system("git checkout " + targetedVersion)
    print()
    print("Switched to version successfully! (If the above output does not show a successful switch, you will have to manually use the 'git checkout <version tag>' command)")
    print("Finished operations.")
except Exception as e:
    print("Error in switching to target version:", e)
    print("To use the version you want, use the comamand 'git checkout <version tag, for e.g 1.0>")
    print("Finished operations.")

