from main import *

@app.route('/identity/create')
def createIdentityPage():
  return render_template('createIdentity.html')

@app.route('/identity/login/')
def loginIdentityPage():
  if 'email' not in request.args:
    return render_template('loginIdentity.html', email="")
  else:
    return render_template('loginIdentity.html', email=request.args['email'])

@app.route('/identity/logout/')
def logout():
  if 'username' not in request.args:
    flash('Username was not provided for identity logout. Failed to perform identity logout.')
    return redirect(url_for('processError'))
  elif 'authToken' not in request.args:
    flash('Authentication token was not provided for identity logout. Failed to perform identity logout.')
    return redirect(url_for('processError'))
  return render_template('logout.html', username=request.args['username'])