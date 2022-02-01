from main import *

@app.route('/portal/session/<certID>/<authToken>/home')
def portalHome(certID, authToken):
    return render_template('portalHome.html')
