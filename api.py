from flask import Flask, request, render_template, Blueprint, send_file, send_from_directory, url_for, redirect
from main import jsonOnly, checkAPIKey, enforceSchema

apiBP = Blueprint('api', __name__)

@apiBP.route("/identity/new", methods=["POST"])
@jsonOnly
@checkAPIKey
@enforceSchema(("identity", int))
def newIdentity():
    return "Success!"