import os, sys, time, datetime, shutil, platform, requests
from dotenv import load_dotenv
load_dotenv()

print("Welcome to Access CheckUp!")
print("This sub-service will check the Access environment for irregularities that may need to be fixed for improved system functionality.")
print()
print("Please wait a while CheckUp scans the system environment (this may take some time)...")
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
## Gather system information
print("Gathering system information...")
print()
time.sleep(2)

def linux_distribution():
  try:
    return platform.linux_distribution()
  except:
    return "N/A"

systemInformation = """Python version: %s
linux_distribution: %s
system: %s
machine: %s
platform: %s
uname: %s
version: %s
mac_ver: %s
""" % (
sys.version.split('\n'),
linux_distribution(),
platform.system(),
platform.machine(),
platform.platform(),
platform.uname(),
platform.version(),
platform.mac_ver(),
)

## Version Compatibility
print("Checking for python version compatibility...")
time.sleep(1.5)
print()
if sys.version_info[0] < 3:
    print(sys.version_info[0])
    print("Python version is too old. Please install Python 3.8 or higher.")
    sys.exit(1)

## Check for required files (ALL OF THEM ONE BY ONE)
print("Checking for required files...this may take quite a second...")
time.sleep(3)

rootFolderEssentialFiles = [
    'accessAnalytics.py',
    'accessStartup.py',
    '.env',
    'AFManager.py',
    'api.py',
    'assets.py',
    'certAuthority.py',
    'copyright.js',
    'emailer.py',
    'emailOTP.py',
    'homepage.html',
    'main.py',
    'models.py',
    'portal.py',
    'admin.py',
    'updater.py'
]

### Root folder essential files check
for filename in rootFolderEssentialFiles:
    if not os.path.isfile(os.path.join(os.getcwd(), filename)):
        critical_issues.append("CRTICIAL ISSUE: The essential file '{}' is not present in the root folder of the Access System. It should be at the path '/{}'.".format(filename, filename))


essentialFoldersCheck = [
    'assets',
    'Chute',
    'templates',
    'supportJSFiles',
    'stylesheets'
]

## Essential root folders check
for folderName in essentialFoldersCheck:
    if not os.path.isdir(os.path.join(os.getcwd(), folderName)):
        critical_issues.append("CRITICAL ISSUE: The essential directory '{}' is not present in the root folder of the Access System. The directory's path should be '/{}'.".format(folderName, folderName))


## Templates folders and files check

templateFoldersAndItsFiles = {
    "emails": [
        'folderRegistered.html',
        'loginEmail.html',
        'otpEmail.html'
    ],
    "portal": [
        'deleteListing.html',
        'folderRegistration.html',
        'newUpload.html',
        'portalFolder.html',
        'portalFolderDeleteFile.html',
        'portalHome.html'
    ],
    "baseFiles": [
        'baseNav.html',
        'baseXNav.html',
        'createIdentity.html',
        'error.html',
        'loginIdentity.html',
        'logout.html',
        'unauthorised.html',
        'version.html',
        'renewSuccess.html'
    ]
}


if not os.path.isdir(os.path.join(os.getcwd(), 'templates')):
    pass
else:
    ### Check for essential folders and files in templates folder
    for dirname in templateFoldersAndItsFiles:
        if dirname == "baseFiles":
            for filename in templateFoldersAndItsFiles[dirname]:
                if not os.path.isfile(os.path.join(os.getcwd(), 'templates', filename)):
                    critical_issues.append("CRTICIAL ISSUE: The essential file '{}' is not present. It should be at the path '/templates/{}'.".format(filename, filename))
            continue
        else:
            if not os.path.isdir(os.path.join(os.getcwd(), 'templates', dirname)):
                critical_issues.append("CRITICAL ISSUE: The sub-directory '{}' is not present in the 'templates' directory. The directory's path should be '/templates/{}'.".format(dirname, dirname))
                continue
            for filename in templateFoldersAndItsFiles[dirname]:
                if not os.path.isfile(os.path.join(os.getcwd(), 'templates', dirname, filename)):
                    critical_issues.append("CRTICIAL ISSUE: The essential file '{}' is not present. It should be at the path '/templates/{}/{}'.".format(filename, dirname, filename))

### Support JS Files check

supportJSFilenames = [
    'createID.js',
    'deleteFile.js',
    'folderRegistration.js',
    'logout.js',
    'portalHome.js',
    'signIn.js'
]

if not os.path.isdir(os.path.join(os.getcwd(), 'supportJSFiles')):
    pass
else:
    for filename in supportJSFilenames:
        if not os.path.isfile(os.path.join(os.getcwd(), 'supportJSFiles', filename)):
            critical_issues.append("CRTICIAL ISSUE: The essential file '{}' is not present. It should be at the path '/supportJSFiles/{}'.".format(filename, filename))

### Assets folder file check

assetsFolderFilenames = [
    'accessLogo.png'
]

if os.path.isdir(os.path.join(os.getcwd(), 'assets')):
    for filename in assetsFolderFilenames:
        if not os.path.isfile(os.path.join(os.getcwd(), 'assets', filename)):
            critical_issues.append("CRTICIAL ISSUE: The essential file '{}' is not present. It should be at the path '/assets/{}'.".format(filename, filename))

### Stylesheets folder check

stylesheetsFilenames = [
    'fancyButtonStyle.css'
]

if os.path.isdir(os.path.join(os.getcwd(), 'stylesheets')):
    for filename in stylesheetsFilenames:
        if not os.path.isfile(os.path.join(os.getcwd(), 'stylesheets', filename)):
            critical_issues.append("CRTICIAL ISSUE: The essential file '{}' is not present. It should be at the path '/stylesheets/{}'.".format(filename, filename))

### NON-ESSENTIAL FILES/FOLDERS CHECK
print()
print("Still working on checking all files...please wait!")
time.sleep(2)

unessentialFoldersNames = [
    'AccessFolders',
    'analyticsReports'
]

for folderName in unessentialFoldersNames:
    if not os.path.isdir(os.path.join(os.getcwd(), folderName)):
        warnings.append("WARNING: The non-essential folder '{}' is not present in the root folder of the Access System. It should be at the path '/{}'".format(folderName, folderName))


### Non essential files check
dataFilenames = [
    'accessIdentities.txt',
    'analyticsData.txt',
    'certificates.txt',
    'validOTPCodes.txt'
]

for filename in dataFilenames:
    if not os.path.isfile(os.path.join(os.getcwd(), filename)):
        warnings.append("WARNING: The non-essential database file '{}' is not present in the root folder of the Access System. It should be at the path '/{}'".format(filename, filename))

######
print()
print("Checking environment variables...")
time.sleep(1)

environmentVariables = [
    'AccessAPIKey',
    'AssignedSystemEmail',
    'AccessEmailPassword',
    'APP_SECRET_KEY',
    'AccessAnalyticsEnabled',
    'RuntimePort'
]

nonessentialEnvVars = [
    'GitpodEnvironment',
    'adminSubdomainEnabled'
]

for envVar in environmentVariables:
    if envVar not in os.environ:
        critical_issues.append("CRITICAL ISSUE: The environment variable '{}' is not present in the .env file. Please rectify the issue by adding it in immediately.".format(envVar))
        continue

    if envVar == "AccessAnalyticsEnabled":
        if os.environ[envVar] not in ['True', 'False']:
            critical_issues.append("CRITICAL ISSUE: An invalid value for the environment variable '{}' was provided. It can either be 'True' or 'False' only.".format(envVar))

for envVar in nonessentialEnvVars:
    if envVar not in os.environ:
        warnings.append("WARNING: The non-essential environment variable '{}' is not present in the .env file.".format(envVar))
        continue
    
    if envVar == "GitpodEnvironment":
        if os.environ[envVar] not in ['True', 'False']:
            warnings.append("WARNING: The non-essential environment variable '{}' has an invalid value. It can either be 'True' or 'False' only.".format(envVar))

### Make request to website and obtain version information
print()
print("Checking current system version...")
time.sleep(2)

if not os.path.isfile(os.path.join(os.getcwd(), 'version.txt')):
    critical_issues.append("CRITICAL ISSUE: The essential 'version.txt' file is not present in the root folder. The current version of the Access System cannot be determined.")
else:
    result = requests.get("https://prakhar896.github.io/meta/access/latestVersion.html")

    try:
        result.raise_for_status()
        with open('version.txt', 'r') as f:
            fileContent = f.read()
            parsedText = result.text.split('>')[1].split('</p')[0]
            if fileContent != parsedText:
                critical_issues.append("VERY CRITICAL ISSUE: This Access System's version is outdated. Current system version: {}, Latest System Version: {}. Please update the system for the best performance. Please refer to the update guide in the Access Startup menu to update the system while still retaining all data.".format(fileContent, parsedText))
    except Exception as e:
        print()
        print("AN ERROR OCCURRED IN CONTACTING THE WEBSITE TO OBTAIN LATEST ACCESS SYTEM VERSION INFORMATION. THE CURRENT SYSTEM VERSION'S OUTDATED STATUS CANNOT BE DETERMINED.")
        print("Error Info: {}".format(e))
        print()
        print("CheckUp will continue anyways...")

print()
print("CheckUp has successfully finished its scan!")

if len(critical_issues) == 0:
    print("There were no critical issues found and so the Access System is safe to boot and is operational.")
else:
    print()
    print("------")
    print("IMPORTANT: There were some critical issues detected in the scan. All of them will be listed below:")
    print()
    for issue in critical_issues:
        print("\t" + issue + "\n")
    
    print()
    print("------")
    print("That is the end of the critical issues detected. Please rectify them immediately otherwise Access Boot is not safe to run and is not operational.")

if len(warnings) == 0:
    print()
    print("There were no warnings found!")
else:
    print()
    print("------")
    print("IMPORTANT: There are some warnings that you should heed attention to. These issues may be resolved by the system itself because it is capable of making its own files in circumstances.")
    print("The warnings are merely issues that you should remember about, the Access System should run fine without you having to fix them.")
    print()
    for warning in warnings:
        print("\t" + warning + "\n")
    print()
    print("------")
    print("That is the end of the warnings detected.")

print()
print()
print("Access CheckUp has successfully completed its operations!")
