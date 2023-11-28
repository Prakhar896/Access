import json, os, shutil, subprocess, random, datetime, copy, base64
from passlib.hash import sha256_crypt as sha
from dotenv import load_dotenv
load_dotenv()

fileUploadLimit = 3
if 'FileUploadsLimit' in os.environ:
  if os.environ['FileUploadsLimit'].isdigit():
    fileUploadLimit = int(os.environ['FileUploadsLimit'])
  else:
    print("MODELS: Could not set FileUploadsLimit. System will fall back on default limit of 3 file uploads.")
    print()
else:
  print("MODELS WARNING: FileUploadsLimit environment variable is not set in .env file. System will fall back on default limit of 3 file uploads.")
  print()

def fileContent(fileName):
  with open(fileName, 'r') as f:
    f_content = f.read()
    return f_content

def generateAuthToken():
  letters_lst = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
  authTokenString = ''
  while len(authTokenString) < 10:
    authTokenString += random.choice(letters_lst)
  return authTokenString

def obtainTargetIdentity(email, accessIdentities):
  targetIdentity = {}
  for username in accessIdentities:
    if accessIdentities[username]['email'] == email:
      targetIdentity = copy.deepcopy(accessIdentities[username])
      targetIdentity["username"] = username
  return targetIdentity

def expireAuthTokens(accessIdentities):
  for username in accessIdentities:
    if (datetime.datetime.now() - datetime.datetime.strptime(accessIdentities[username]['last-login-date'], Universal.systemWideStringDateFormat)).total_seconds() >= 10800:
      try:
        if 'loggedInAuthToken' in accessIdentities[username]:
          del accessIdentities[username]['loggedInAuthToken']
          print("Models: Expired auth token for username {}".format(username))
      except Exception as e:
        print("Models: Failed to expire auth token. {}".format(e))
  return accessIdentities

class Encryption:
  @staticmethod
  def encodeToB64(inputString):
    hash_bytes = inputString.encode("ascii")
    b64_bytes = base64.b64encode(hash_bytes)
    b64_string = b64_bytes.decode("ascii")
    return b64_string
    
  @staticmethod
  def decodeFromB64(encodedHash):
    b64_bytes = encodedHash.encode("ascii")
    hash_bytes = base64.b64decode(b64_bytes)
    hash_string = hash_bytes.decode("ascii")
    return hash_string
  
  @staticmethod
  def isBase64(encodedHash):
    try:
      hashBytes = encodedHash.encode("ascii")
      return base64.b64encode(base64.b64decode(hashBytes)) == hashBytes
    except Exception:
      return False

  @staticmethod
  def encodeToSHA256(string):
    return sha.hash(string)
  
  @staticmethod
  def verifySHA256(inputString, hash):
    return sha.verify(inputString, hash)
  
  @staticmethod
  def convertBase64ToSHA(base64Hash):
    return Encryption.encodeToSHA256(Encryption.decodeFromB64(base64Hash))

class Universal:
  systemWideStringDateFormat = '%Y-%m-%d %H:%M:%S'
  version = None

  @staticmethod
  def getVersion():
    if not os.path.isfile(os.path.join(os.getcwd(), 'version.txt')):
      return "Version File Not Found"
    else:
      with open('version.txt', 'r') as f:
        fileData = f.read()
        Universal.version = fileData
        return fileData

class Logger:
  @staticmethod
  def checkPermission():
      if "LoggingEnabled" in os.environ and os.environ["LoggingEnabled"] == 'True':
          return True
      else:
          return False

  @staticmethod
  def setup():
      if Logger.checkPermission():
          try:
              if not os.path.exists(os.path.join(os.getcwd(), "logs.txt")):
                  with open("logs.txt", "w") as f:
                      f.write("{}UTC {}\n".format(datetime.datetime.now().utcnow().strftime(Universal.systemWideStringDateFormat), "LOGGER: Logger database file setup complete."))
          except Exception as e:
              print("LOGGER SETUP ERROR: Failed to setup logs.txt database file. Setup permissions have been granted. Error: {}".format(e))

      return

  @staticmethod
  def log(message):
      if Logger.checkPermission():
          try:
              with open("logs.txt", "a") as f:
                  f.write("{}UTC {}\n".format(datetime.datetime.now().utcnow().strftime(Universal.systemWideStringDateFormat), message))
          except Exception as e:
              print("LOGGER LOG ERROR: Failed to log message. Error: {}".format(e))
        
      return
    
  @staticmethod
  def destroyAll():
      try:
          if os.path.exists(os.path.join(os.getcwd(), "logs.txt")):
              os.remove("logs.txt")
      except Exception as e:
          print("LOGGER DESTROYALL ERROR: Failed to destroy logs.txt database file. Error: {}".format(e))

  @staticmethod
  def readAll():
      if not Logger.checkPermission():
          return "ERROR: Logging-related services do not have permission to operate."
      try:
          if os.path.exists(os.path.join(os.getcwd(), "logs.txt")):
              with open("logs.txt", "r") as f:
                  logs = f.readlines()
                  for logIndex in range(len(logs)):
                      logs[logIndex] = logs[logIndex].replace("\n", "")
                  return logs
          else:
              return []
      except Exception as e:
          print("LOGGER READALL ERROR: Failed to check and read logs.txt database file. Error: {}".format(e))
          return "ERROR: Failed to check and read logs.txt database file. Error: {}".format(e)
      
  @staticmethod
  def manageLogs():
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
        allLogs = Logger.readAll()

        userChoice = userChoice.split(" ")
        logCount = 0
        if len(userChoice) != 1:
          try:
            logCount = int(userChoice[1])
            if logCount > len(allLogs):
              logCount = len(allLogs)
            elif logCount <= 0:
              raise Exception("Invalid log count. Must be a positive integer above 0 lower than or equal to the total number of logs.")
          except Exception as e:
            print("LOGGER: Failed to read logs. Error: {}".format(e))
            continue
        else:
          logCount = len(allLogs)

        targetLogs = allLogs[-logCount:]
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