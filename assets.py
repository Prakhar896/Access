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