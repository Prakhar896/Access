from flask import Flask, request
from flask_cors import CORS
import json, random, time, sys, subprocess, os, shutil
import datetime
msUsername = os.environ['msUsername']
msPassword = os.environ['msPassword']
loginUsername = os.environ['loginUsername']
loginPassword = os.environ['loginPassword']
accessCode = os.environ['accessCode']

app = Flask(__name__)
CORS(app)

with open('validAuthTokens.txt', 'r') as f:
  validAuthTokens = json.load(f)

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

def checkIfPastExpiryDate():
  present = datetime.datetime.now()
  isExpired = datetime.datetime(2021,12, 1) < present
  return isExpired

@app.route('/')
def home():
  return fileContent('homepage.html')

@app.route('/login/<username>/<password>')
def login(username, password):
  if username != loginUsername or password != loginPassword:
    return "<h1>Incorrect Username and Password. Please try again!</h1>"
  validAuthTokens[datetime.datetime.now().strftime('%H:%M:%S')] = generateAuthToken()
  json.dump(validAuthTokens, open('validAuthTokens.txt', 'w'))
  return fileContent('processing.html')

@app.route('/getToken', methods=['POST'])
def getToken():
  if request.headers['Content-Type'] != 'application/json' or request.headers['AccessCode'] != accessCode:
    return "Invalid request. Please try again."
  if len(validAuthTokens) == 0:
    return "No valid active auth tokens available."
  if checkIfPastExpiryDate():
    return "Login Certificate Identity is expired. You cannot access the information anymore."
  tokenToReturn = ''
  for token in validAuthTokens:
    tokenToReturn = validAuthTokens[token]
    break
  return tokenToReturn

@app.route('/data/<authToken>')
def showData(authToken):
  isValid = False
  print(validAuthTokens)
  for timeKey in validAuthTokens:
    if validAuthTokens[timeKey] == authToken:
      isValid = True
  if not isValid:
    return "<h1>Invalid auth token. Please obtain a new auth token by logging in with your Access Identity.</h1>"
  elif checkIfPastExpiryDate():
    return "<h1>Login Certificate Identity is expired. You cannot access the information anymore.</h1>"
  # return fileContent('data.html')
  td = datetime.datetime(2021, 12, 1) - datetime.datetime.now()
  contentToReturn = """
  <head>
  <script src="https://unpkg.com/axios/dist/axios.min.js">
	</script>
  </head>
  <h1>MINECRAFT ACCOUNT LOGIN INFORMATION</h1>
  <p>Username: %s</p>
  <p>Password: %s</p>
  <p>Additional Message: jai hi, nice u made it to this site, okay so with this login information you have to go to minecraft.net, login, then go to my profile and then click download installer, from where you will download the minecraft launcher and u can start playing :D</p>
  <p>----------</p>
  <h3>Auth Session Metadata</h6>
  <p>AUTH SESSION: ACTIVE, CLIENT ID: 3238r9f3t48gtvd82.portable</p>
  <p>Static Port open: 1800</p>
  <p>Certificate Identity Security Maintained: 1</p>
  <p>Time until access identity expiration: %d days and %d seconds</p>
  <script>
  window.onbeforeunload = function() {
    // Do something
    axios({
      method: 'get',
      url: 'https://access.drakonzai.repl.co/clearTokens',
      headers: {},
      data: {}
    }).then(response => {
      if (response.data == 'Cleared Tokens!') {
        console.log('Successfully cleared tokens!')
      } else {
        console.log("Couldnt clear tokens!")
      }
    })
  }
  </script>
  """ % (msUsername, msPassword, td.days, td.seconds)
# .format(msUsername, msPassword, td.days, td.seconds)
  return contentToReturn

@app.route('/clearTokens')
def clearTokens():
  global validAuthTokens
  validAuthTokens = {}
  json.dump(validAuthTokens, open('validAuthTokens.txt', 'w'))
  return "Cleared Tokens!"

# assets
@app.route('/assets/copyright')
def copyright():
  return fileContent('copyright.js')

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8000, threaded=True)
