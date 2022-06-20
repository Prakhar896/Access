import json, os, shutil, subprocess, random, datetime, copy
from dotenv import load_dotenv
load_dotenv()

systemWideStringDateFormat = '%Y-%m-%d %H:%M:%S'
fileUploadLimit = 3
if 'FileUploadsLimit' in os.environ:
  if os.environ['FileUploadsLimit'].isdigit():
    fileUploadLimit = int(os.environ['FileUploadsLimit'])
  else:
    print("-------")
    print("MODELS ERROR: Could not set FileUploadsLimit. System will fall back on default upload limit of 3 files.")
    print("-------")
    print()
    print()
else:
  print("-------")
  print("MODELS WARNING: FileUploadsLimit is NOT SET in the .env file. System will fall back on default upload limit of 3 files.")
  print("-------")
  print()
  print()

def fileContent(fileName):
  with open(fileName, 'r') as f:
    f_content = f.read()
    return f_content

def generateAuthToken():
  letters_lst = ['a', 'e', 'w', 't', 'a', 'u', 'o', 'p', '2', '5', '6', '3', '8', '4']
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
    if (datetime.datetime.now() - datetime.datetime.strptime(accessIdentities[username]['last-login-date'], systemWideStringDateFormat)).total_seconds() >= 10800:
      try:
        if 'loggedInAuthToken' in accessIdentities[username]:
          del accessIdentities[username]['loggedInAuthToken']
          print("Models: Expired auth token for username {}".format(username))
      except Exception as e:
        print("Models: Failed to expire auth token. {}".format(e))
  return accessIdentities
