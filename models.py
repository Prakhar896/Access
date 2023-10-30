import json, os, shutil, subprocess, random, datetime, copy, base64
from passlib.hash import sha256_crypt as sha

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