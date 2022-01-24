from main import *

@app.route('/api/createIdentity', methods=['POST'])
def makeAnIdentity():
    if 'Content-Type' not in request.headers and 'AccessAPIKey' not in request.headers:
        return "ERROR: One or more headers were not present in the API request. Request failed."
    if request.headers['Content-Type'] == 'application/json' and request.headers['AccessAPIKey'] == os.environ['AccessAPIKey']:
        if 'username' not in request.json:
            return "ERROR: New identity username field not present in body. Request failed."
        if 'password' not in request.json:
            return "ERROR: New identity password field not present in body. Request failed."
    else:
        return "ERROR: One or more of the request headers had incorrect values for this request. Request failed."