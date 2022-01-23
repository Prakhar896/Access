from main import *

@app.route('/assets/copyright')
def copyright():
  return fileContent('copyright.js')