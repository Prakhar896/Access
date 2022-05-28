from main import *

@app.route('/assets/copyright')
def copyright():
  return fileContent('copyright.js')

@app.route('/assets/fancyButtons')
def fancyButtonsCSS():
  return fileContent('stylesheets/fancyButtonStyle.css')

@app.route('/assets/createIDJS')
def createIDJS():
  return fileContent('supportJSFiles/createID.js')

@app.route('/assets/accessLogo')
def accessLogoIMG():
  # Send accessLogo.png image
  return send_file('assets/accessLogo.png', mimetype='image/png')

@app.route('/assets/signinJS')
def signinJS():
  return fileContent('supportJSFiles/signIn.js')

@app.route('/assets/portalHomeJS')
def portalHomeJS():
  return fileContent('supportJSFiles/portalHome.js')

@app.route('/assets/folderRegistrationJS')
def folderRegistrationJS():
  return fileContent('supportJSFiles/folderRegistration.js')

@app.route('/assets/logoutJS')
def logoutJS():
  return fileContent('supportJSFiles/logout.js')

@app.route('/assets/deleteFileJS')
def deleteFileJS():
  return fileContent('supportJSFiles/deleteFile.js')

@app.route('/assets/emailPrefJS')
def emailPrefJS():
  return fileContent('supportJSFiles/emailPref.js')

@app.route('/assets/updateEmailConfirmationJS')
def updateEmailConfirmationJS():
  return fileContent('supportJSFiles/updateEmailConfirmation.js')