from main import fileContent
from flask import send_file, Blueprint

assetsBP = Blueprint('assets', __name__)

@assetsBP.route('/assets/copyright')
def copyright():
    return fileContent('copyright.js')

@assetsBP.route('/assets/fancyButtons')
def fancyButtonsCSS():
    return fileContent('stylesheets/fancyButtonStyle.css')

@assetsBP.route('/assets/createIDJS')
def createIDJS():
    return fileContent('supportJSFiles/createID.js')

@assetsBP.route('/assets/accessLogo')
def accessLogoIMG():
    # Send accessLogo.png image
    return send_file('assets/accessLogo.png', mimetype='image/png')

@assetsBP.route('/assets/signinJS')
def signinJS():
    return fileContent('supportJSFiles/signIn.js')

@assetsBP.route('/assets/portalHomeJS')
def portalHomeJS():
    return fileContent('supportJSFiles/portalHome.js')

@assetsBP.route('/assets/folderRegistrationJS')
def folderRegistrationJS():
    return fileContent('supportJSFiles/folderRegistration.js')

@assetsBP.route('/assets/logoutJS')
def logoutJS():
    return fileContent('supportJSFiles/logout.js')

@assetsBP.route('/assets/deleteFileJS')
def deleteFileJS():
    return fileContent('supportJSFiles/deleteFile.js')

@assetsBP.route('/assets/emailPrefJS')
def emailPrefJS():
    return fileContent('supportJSFiles/emailPref.js')

@assetsBP.route('/assets/updateEmailConfirmationJS')
def updateEmailConfirmationJS():
    return fileContent('supportJSFiles/updateEmailConfirmation.js')

@assetsBP.route('/assets/updatePasswordJS')
def updatePasswordJS():
    return fileContent('supportJSFiles/updatePassword.js')

@assetsBP.route('/assets/deleteIdentityJS')
def deleteIdentityJS():
    return fileContent('supportJSFiles/deleteIdentity.js')

@assetsBP.route('/assets/passwordResetJS')
def passwordResetJS():
    return fileContent('supportJSFiles/passwordReset.js')