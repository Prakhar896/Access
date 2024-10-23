import json, os, shutil, subprocess, random, datetime, copy, base64, uuid
from passlib.hash import sha256_crypt as sha
from addons import *
from dotenv import load_dotenv
load_dotenv()

def fileContent(filePath, passAPIKey=False):
    with open(filePath, 'r') as f:
        f_content = f.read()
        if passAPIKey:
            f_content = f_content.replace("\{{ API_KEY }}", os.getenv("API_KEY"))
        return f_content

def customRenderTemplate(filePath, **kwargs):
    with open(filePath, 'r') as f:
        f_content = f.read()
        for key in kwargs:
            f_content = f_content.replace("{{ " + key + " }}", kwargs[key])
        return f_content

    
# DatabaseInterface class
class DI:
    '''## INTRO
    This class (DatabaseInterface) is to provide a simple interface to work with the database.

    All you need to do is run the `setup` method and then you are good to go. `DI` will handle all the grunt work for you, especially if you have enabled Firebase RTDB. `DI.data` is a dictionary representing the database that you can freely manipulate.
    
    ## Usage:
    ```
    from models import DI
    DI.setup()

    ## Let's create a new account under the 'accounts' top-level key
    DI.data["accounts"]["newAccountID"] = {"name": "John Appleseed"}

    ## Saves the changes to both local and cloud (if enabled) databases
    DI.save()
    ```

    ## ADVANCED:
    Initially, `DI.data` is a list to indicate to DI itself that it is not set-up and that a database has not been loaded onto memory. Only after setup does it becomes a dictionary.

    The `setup` method creates the database file if it does not exist, and loads the database file into memory. If enabled, it connects to Firebase Realtime Database via `FireRTDB` and loads the database from there instead.

    DI makes loading a 'cloud-first' strategy; it over-writes the local database with the data it fetched from Firebase RTDB. However, DI carries out a 'local-first' strategy during save; it over-writes the cloud database with the data it has in memory. Auto-repair mechanisms are in place to minimise data loss.

    ## INTEGRATING FIREBASE RTDB:
    
    DI uses `FireRTDB` to work with Firebase RTBD. In order to activate the cloud database integration, you need the following:
    - `FireConnEnabled` set to `True` in the `.env` file
    - `FireRTDBEnabled` set to `True` in the `.env` file
    - `RTDB_URL` set to the URL of your Firebase RTDB in the `.env` file (obtain via going to Realtime Database on the Firebase console)
    - `serviceAccountKey.json` file in the root directory of the project (obtain via going to Project Settings > Service Accounts on the Firebase console)
    '''

    data = []
    syncStatus = True
    file = "database.json"

    sampleData = {
        
    }

    @staticmethod
    def setup():
        if not os.path.exists(os.path.join(os.getcwd(), DI.file)):
            with open(DI.file, "w") as f:
                json.dump(DI.sampleData, f)
        
        if FireRTDB.checkPermissions():
            try:
                if not FireConn.connected:
                    print("DI-FIRECONN: Firebase connection not established. Attempting to connect...")
                    response = FireConn.connect()
                    if response != True:
                        print("DI-FIRECONN: Failed to connect to Firebase. Aborting setup.")
                        return response
                    else:
                        print("DI-FIRECONN: Firebase connection established. Firebase RTDB is enabled.")
                else:
                    print("DI: Firebase RTDB is enabled.")
            except Exception as e:
                print("DI FIRECONN ERROR: " + str(e))
                return "Error"
            
        return DI.load()
    
    @staticmethod
    def load():
        try:
            ## Check and create database file if it does not exist
            if not os.path.exists(os.path.join(os.getcwd(), DI.file)):
                with open(DI.file, "w") as f:
                    json.dump(DI.sampleData, f)

            def loadFromLocalDBFile():
                loadedData = []
                # Read data from local database file
                with open(DI.file, "r") as f:
                    loadedData = json.load(f)

                ## Carry out structure enforcement
                changesMade = False
                for topLevelKey in DI.sampleData:
                    if topLevelKey not in loadedData:
                        loadedData[topLevelKey] = DI.sampleData[topLevelKey]
                        changesMade = True

                if changesMade:
                    # Local database structure needs to be updated
                    with open(DI.file, "w") as f:
                        json.dump(loadedData, f)

                # Load data into DI
                DI.data = loadedData
                return

            if FireRTDB.checkPermissions():
                # Fetch data from RTDB
                fetchedData = FireRTDB.getRef()
                if isinstance(fetchedData, str) and fetchedData.startswith("ERROR"):
                    # Trigger last resort of local database (Auto-repair)
                    print("DI-FIRERTDB GETREF ERROR: " + fetchedData)
                    print("DI: System will try to resort to local database to load data to prevent a crash. Attempts to sync with RTDB will continue.")

                    loadFromLocalDBFile()
                    DI.syncStatus = False
                    return "Success"
                
                # Translate data for local use
                fetchedData = FireRTDB.translateForLocal(fetchedData)
                if isinstance(fetchedData, str) and fetchedData.startswith("ERROR"):
                    # Trigger last resort of local database (Auto-repair)
                    print("DI-FIRERTDB TRANSLATELOCAL ERROR: " + fetchedData)
                    print("DI: System will try to resort to local database to load data to prevent a crash. Attempts to sync with RTDB will continue.")

                    loadFromLocalDBFile()
                    DI.syncStatus = False
                    return "Success"
                
                # Carry out structure enforcement
                changesMade = False
                for topLevelKey in DI.sampleData:
                    if topLevelKey not in fetchedData:
                        fetchedData[topLevelKey] = DI.sampleData[topLevelKey]
                        changesMade = True

                if changesMade:
                    # RTDB structure needs to be updated
                    response = FireRTDB.setRef(FireRTDB.translateForCloud(fetchedData))
                    if response != True:
                        print("DI-FIRERTDB SETREF ERROR: " + response)
                        print("DI: Failed to update RTDB structure. System will continue to avoid a crash but attempts to sync with RTDB will continue.")
                        DI.syncStatus = False

                # Write data to local db file
                with open(DI.file, "w") as f:
                    json.dump(fetchedData, f)
                
                # Load data into DI
                DI.data = fetchedData
            else:
                loadFromLocalDBFile()
                DI.syncStatus = True
                return "Success"
        except Exception as e:
            print("DI ERROR: Failed to load data from database; error: {}".format(e))
            return "Error"
        return "Success"
    
    @staticmethod
    def save():
        try:
            with open(DI.file, "w") as f:
                json.dump(DI.data, f)
            DI.syncStatus = True

            # Update RTDB
            if FireRTDB.checkPermissions():
                response = FireRTDB.setRef(FireRTDB.translateForCloud(DI.data))
                if response != True:
                    print("DI FIRERTDB SETREF ERROR: " + response)
                    print("DI: System will resort to local database to prevent a crash. Attempts to sync with RTDB will continue.")
                    DI.syncStatus = False
                    # Continue runtime as system can function without cloud database
        except Exception as e:
            print("DI ERROR: Failed to save data to database; error: {}".format(e))
            DI.syncStatus = False
            return "Error"
        return "Success"
    
class Encryption:
    @staticmethod
    def encodeToB64(inputString):
        '''Encodes a string to base64'''
        hash_bytes = inputString.encode("ascii")
        b64_bytes = base64.b64encode(hash_bytes)
        b64_string = b64_bytes.decode("ascii")
        return b64_string
    
    @staticmethod
    def decodeFromB64(encodedHash):
        '''Decodes a base64 string to a string'''
        b64_bytes = encodedHash.encode("ascii")
        hash_bytes = base64.b64decode(b64_bytes)
        hash_string = hash_bytes.decode("ascii")
        return hash_string
  
    @staticmethod
    def isBase64(encodedHash):
        '''Checks if a string is base64'''
        try:
            hashBytes = encodedHash.encode("ascii")
            return base64.b64encode(base64.b64decode(hashBytes)) == hashBytes
        except Exception:
            return False

    @staticmethod
    def encodeToSHA256(string):
        '''Encodes a string to SHA256'''
        return sha.hash(string)
  
    @staticmethod
    def verifySHA256(inputString, hash):
        '''Verifies a string against a SHA256 hash using the `sha` module directly'''
        return sha.verify(inputString, hash)
  
    @staticmethod
    def convertBase64ToSHA(base64Hash):
        '''Converts a base64 string to a SHA256 hash'''
        return Encryption.encodeToSHA256(Encryption.decodeFromB64(base64Hash))
    
class Universal:
    '''This class contains universal methods and variables that can be used across the entire project. Project-wide standards and conventions (such as datetime format) are also defined here.'''

    systemWideStringDatetimeFormat = "%Y-%m-%d %H:%M:%S"
    copyright = "© 2024 NYP AI. All Rights Reserved."

    @staticmethod
    def generateUniqueID(customLength=None):
        if customLength == None:
            return uuid.uuid4().hex
        else:
            source = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            return ''.join(random.choices(source, k=customLength))
    
    @staticmethod
    def utcNow():
        return datetime.datetime.now(datetime.timezone.utc)
    
    @staticmethod
    def utcNowString():
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
        
class Logger:
    file = "logs.txt"
    
    '''## Intro
    A class offering silent and quick logging services.

    Explicit permission must be granted by setting `LOGGING_ENABLED` to `True` in the `.env` file. Otherwise, all logging services will be disabled.
    
    ## Usage:
    ```
    Logger.setup() ## Optional

    Logger.log("Hello world!") ## Adds a log entry to the logs.txt database file, if permission was granted.
    ```

    ## Advanced:
    Activate Logger's management console by running `Logger.manageLogs()`. This will allow you to read and destroy logs in an interactive manner.
    '''
    
    @staticmethod
    def checkPermission():
        return "LOGGING_ENABLED" in os.environ and os.environ["LOGGING_ENABLED"] == 'True'

    @staticmethod
    def setup():
        if Logger.checkPermission():
            try:
                if not os.path.exists(os.path.join(os.getcwd(), Logger.file)):
                    with open(Logger.file, "w") as f:
                        f.write("{}UTC {}\n".format(Universal.utcNowString(), "LOGGER: Logger database file setup complete."))
            except Exception as e:
                print("LOGGER SETUP ERROR: Failed to setup logs.txt database file. Setup permissions have been granted. Error: {}".format(e))

        return

    @staticmethod
    def log(message, debugPrintExplicitDeny=False):
        if "DEBUG_MODE" in os.environ and os.environ["DEBUG_MODE"] == 'True' and (not debugPrintExplicitDeny):
            print("LOG: {}".format(message))
        if Logger.checkPermission():
            try:
                with open(Logger.file, "a") as f:
                    f.write("{}UTC {}\n".format(Universal.utcNowString(), message))
            except Exception as e:
                print("LOGGER LOG ERROR: Failed to log message. Error: {}".format(e))
        
        return
    
    @staticmethod
    def destroyAll():
        try:
            if os.path.exists(os.path.join(os.getcwd(), Logger.file)):
                os.remove(Logger.file)
        except Exception as e:
            print("LOGGER DESTROYALL ERROR: Failed to destroy logs.txt database file. Error: {}".format(e))

    @staticmethod
    def readAll(explicitLogsFile=None):
        if not Logger.checkPermission():
            return "ERROR: Logging-related services do not have permission to operate."
        logsFile = Logger.file if explicitLogsFile == None else explicitLogsFile
        try:
            if os.path.exists(os.path.join(os.getcwd(), logsFile)):
                with open(logsFile, "r") as f:
                    logs = f.readlines()
                    for logIndex in range(len(logs)):
                        logs[logIndex] = logs[logIndex].replace("\n", "")
                    return logs
            else:
                return []
        except Exception as e:
            print("LOGGER READALL ERROR: Failed to check and read logs file. Error: {}".format(e))
            return "ERROR: Failed to check and read logs file. Error: {}".format(e)
      
    @staticmethod
    def manageLogs(explicitLogsFile=None):
        permission = Logger.checkPermission()
        if not permission:
            print("LOGGER: Logging-related services do not have permission to operate. Set LoggingEnabled to True in .env file to enable logging.")
            return
    
        print("LOGGER: Welcome to the Logging Management Console.")
        while True:
            print("""
Commands:
    read <number of lines, e.g 50 (optional)>: Reads the last <number of lines> of logs. If no number is specified, all logs will be displayed.
    destroy: Destroys all logs.
    exit: Exit the Logging Management Console.
""")
    
            userChoice = input("Enter command: ")
            userChoice = userChoice.lower()
            while not userChoice.startswith("read") and (userChoice != "destroy") and (userChoice != "exit"):
                userChoice = input("Invalid command. Enter command: ")
                userChoice = userChoice.lower()
    
            if userChoice.startswith("read"):
                allLogs = Logger.readAll(explicitLogsFile=explicitLogsFile)
                targetLogs = []

                userChoice = userChoice.split(" ")

                # Log filtering feature
                if len(userChoice) == 1:
                    targetLogs = allLogs
                elif userChoice[1] == ".filter":
                    if len(userChoice) < 3:
                        print("Invalid log filter. Format: read .filter <keywords>")
                        continue
                    else:
                        try:
                            keywords = userChoice[2:]
                            for log in allLogs:
                                logTags = log[23::]
                                logTags = logTags[:logTags.find(":")].upper().split(" ")

                                ## Check if log contains all keywords
                                containsAllKeywords = True
                                for keyword in keywords:
                                    if keyword.upper() not in logTags:
                                        containsAllKeywords = False
                                        break
                                
                                if containsAllKeywords:
                                    targetLogs.append(log)
                                
                            print("Filtered logs with keywords: {}".format(keywords))
                            print()
                        except Exception as e:
                            print("LOGGER: Failed to parse and filter logs. Error: {}".format(e))
                            continue
                else:
                    logCount = 0
                    try:
                        logCount = int(userChoice[1])
                        if logCount > len(allLogs):
                            logCount = len(allLogs)
                        elif logCount <= 0:
                            raise Exception("Invalid log count. Must be a positive integer above 0 lower than or equal to the total number of logs.")
                        
                        targetLogs = allLogs[-logCount::]
                    except Exception as e:
                        print("LOGGER: Failed to read logs. Error: {}".format(e))
                        continue

                logCount = len(targetLogs)
                print()
                print("Displaying {} log entries:".format(logCount))
                print()
                for log in targetLogs:
                    print("\t{}".format(log))
            elif userChoice == "destroy":
                Logger.destroyAll()
                print("LOGGER: All logs destroyed.")
            elif userChoice == "exit":
                print("LOGGER: Exiting Logging Management Console...")
                break
    
        return