from flask import Blueprint, request, jsonify
from main import configManager
from decorators import admin

panelBP = Blueprint('panel', __name__)

@panelBP.route('/<accessKey>', methods=['GET'])
@admin
def panelActions():
    return "SUCCESS: Welcome admin."