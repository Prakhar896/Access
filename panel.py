from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from services import Universal
from decorators import admin

panelBP = Blueprint('panel', __name__)

@panelBP.route('/<accessKey>')
def panel(accessKey):
    return redirect(url_for('panel.options', accessKey=accessKey))

@panelBP.route('/<accessKey>/home', methods=['GET'])
@admin
def options():
    return render_template('panel.html')

@panelBP.route('/<accessKey>/toggleLock', methods=['GET'])
@admin
def toggleLock():
    Universal.configManager.config["systemLock"] = not Universal.configManager.getSystemLock()
    Universal.configManager.dump()
    
    return "SUCCESS: System lock toggled to '{}'.".format(Universal.configManager.getSystemLock())