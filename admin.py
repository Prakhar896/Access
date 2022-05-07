from main import *

@app.route('/', subdomain='admin')
def adminHome():
    return "<h1>Hello, this is the Admin Subdomain</h1>"