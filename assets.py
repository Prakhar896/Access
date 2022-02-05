from main import *

@app.route('/assets/copyright')
def copyright():
  return fileContent('copyright.js')

@app.route('/assets/fancyButtons')
def fancyButtonsCSS():
  return fileContent('fancyButtonStyle.css')

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