import os, sys, shutil, json, copy, datetime, random
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

identityMetaBP = Blueprint('identityMeta', __name__)

@identityMetaBP.route('/identity/create')
def createIdentityPage():
  return render_template('createIdentity.html')

@identityMetaBP.route('/identity/login/')
def loginIdentityPage():
  if 'email' not in request.args:
    return render_template('loginIdentity.html', email="")
  else:
    return render_template('loginIdentity.html', email=request.args['email'])

@identityMetaBP.route('/identity/logout/')
def logout():
  if 'username' not in request.args:
    flash('Username was not provided for identity logout. Failed to perform identity logout.')
    return redirect(url_for('processError'))
  elif 'authToken' not in request.args:
    flash('Authentication token was not provided for identity logout. Failed to perform identity logout.')
    return redirect(url_for('processError'))
  return render_template('logout.html', username=request.args['username'])

@identityMetaBP.route('/identity/passwordReset')
def passwordReset():
    return render_template('passwordReset.html')