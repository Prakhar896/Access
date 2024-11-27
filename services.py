import os, json, base64, random, datetime, uuid, functools
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
from passlib.hash import sha256_crypt as sha
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

class Trigger:
    '''
    A class to define triggers for `APScheduler` based jobs.
    
    Implementation variations:
    ```python
    from apscheduler.triggers.date import DateTrigger
    import datetime
    from services import Trigger
    
    ## Immediate trigger
    immediateTrigger = Trigger()
    
    ## Interval trigger
    intervalTrigger = Trigger(type='interval', seconds=5, minutes=3, hours=2) # Triggers every 2 hours 3 minutes and 5 seconds (cumulatively)
    
    ## Date trigger
    dateTrigger = Trigger(type='date', triggerDate=(datetime.datetime.now() + datetime.timedelta(seconds=5))) # Triggers 5 seconds later
    
    ## Custom trigger
    customTrigger = Trigger(customAPTrigger=DateTrigger(run_date=(datetime.datetime.now() + datetime.timedelta(seconds=5))) # Custom APScheduler trigger
    ```
    '''
    
    def __init__(self, type='interval', seconds=None, minutes=None, hours=None, triggerDate: datetime.datetime=None, customAPTrigger: BaseTrigger=None) -> None:
        self.type = type
        self.immediate = seconds == None and minutes == None and hours == None and triggerDate == None
        self.seconds = seconds if seconds != None else 0
        self.minutes = minutes if minutes != None else 0
        self.hours = hours if hours != None else 0
        self.triggerDate = triggerDate
        self.customAPTrigger = customAPTrigger

class AsyncProcessor:
    """
    Async processor uses the `apscheduler` library to run functions asynchronously. Specific intervals can be set if needed as well.
    
    Manipulate the underling scheduler with the `scheduler` attribute.
    
    Sample Usage:
    ```python
    asyncProcessor = AsyncProcessor()
    
    def greet():
        print("Hi!")
    
    jobID = asyncProcessor.addJob(greet, trigger=Trigger(type='interval', seconds=5)) # This is all you need to add the job
    
    ## Pausing the scheduler
    asyncProcessor.pause()
    
    ## Resuming the scheduler
    asyncProcessor.resume()
    
    ## Shutting down the scheduler
    asyncProcessor.shutdown()
    
    ## To stop a job, use the jobID
    asyncProcessor.scheduler.remove_job(jobID) ## .pause_job() and .resume_job() can also be used to manipulate the job itself
    
    ## Disable logging with Logger
    asyncProcessor.logging = False
    ```
    
    For trigger options, see the `Trigger` class.
    """
    
    def __init__(self, paused=False, logging=True) -> None:
        self.id = uuid.uuid4().hex
        self.scheduler = BackgroundScheduler()
        self.scheduler.start(paused=paused)
        self.logging = logging
        
        self.log("Scheduler initialised in {} mode.".format("paused" if paused else "active"))
        
    def log(self, message):
        if self.logging == True:
            Logger.log("ASYNCPROCESSOR: {}: {}".format(self.id, message))
    
    def shutdown(self):
        self.scheduler.shutdown()
        self.log("Scheduler shutdown.")
    
    def pause(self):
        self.scheduler.pause()
        self.log("Scheduler paused.")
    
    def resume(self):
        self.scheduler.resume()
        self.log("Scheduler resumed.")
    
    def addJob(self, function, *args, trigger: Trigger=None, **kwargs):
        """
        Adds a job to the scheduler.
        """
        if trigger == None: trigger = Trigger()
        
        job = None
        if trigger.customAPTrigger != None:
            job = self.scheduler.add_job(function, trigger.customAPTrigger, args=args, kwargs=kwargs)
            self.log("Job for '{}' added with custom trigger.".format(function.__name__))
        elif trigger.immediate:
            job = self.scheduler.add_job(function, args=args, kwargs=kwargs)
            self.log("Job for '{}' added with immediate trigger.".format(function.__name__))
        elif trigger.type == "date":
            job = self.scheduler.add_job(function, DateTrigger(run_date=trigger.triggerDate), args=args, kwargs=kwargs)
            self.log("Job for '{}' added with trigger date: {}.".format(function.__name__, trigger.triggerDate.isoformat()))
        else:
            job = self.scheduler.add_job(function, 'interval', seconds=trigger.seconds, minutes=trigger.minutes, hours=trigger.hours, args=args, kwargs=kwargs)
            self.log("Job for '{}' added with trigger: {} seconds, {} minutes, {} hours.".format(function.__name__, trigger.seconds, trigger.minutes, trigger.hours))
            
        return job.id

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
    copyright = "© 2024 Prakhar Trivedi. All Rights Reserved."
    version = None
    configManager: Config = Config()
    asyncProcessor: AsyncProcessor = None
    store = {}
    
    @staticmethod
    def initAsync():
        Universal.asyncProcessor = AsyncProcessor()
    
    @staticmethod
    def getVersion():
        if Universal.version != None:
            return Universal.version
        if not os.path.isfile(os.path.join(os.getcwd(), 'version.txt')):
            return "Version File Not Found"
        else:
            with open('version.txt', 'r') as f:
                fileData = f.read()
                Universal.version = fileData
                return fileData

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
    
    @staticmethod
    def fromUTC(utcString):
        return datetime.datetime.fromisoformat(utcString)
        
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
                                logTags = log[36::]
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