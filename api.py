from flask import Flask, request, render_template, Blueprint, send_file, send_from_directory, url_for, redirect
from main import jsonOnly, checkAPIKey

apiBP = Blueprint('api', __name__)

@apiBP.route("/identity/new", methods=["POST"])
@jsonOnly
@checkAPIKey
def newIdentity():
    pass