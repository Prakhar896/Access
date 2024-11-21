from flask import Flask, Blueprint, redirect, render_template, request, url_for

frontendBP = Blueprint('frontend', __name__)

@frontendBP.route('/')
def homepage():
    return 'A better access is coming soon.'

@frontendBP.route('/verifyEmail', methods=["GET"])
def verifyEmail():
    return redirect(url_for('frontend.homepage'))