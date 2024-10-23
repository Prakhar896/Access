from flask import Flask, request, render_template, Blueprint, send_file, send_from_directory, url_for, redirect

apiBP = Blueprint('api', __name__)

# Coming soon