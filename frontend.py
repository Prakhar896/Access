from flask import Flask, Blueprint, redirect, render_template, request, url_for

frontendBP = Blueprint('frontend', __name__)

@frontendBP.route('/')
def homepage():
    return render_template("index.html")

@frontendBP.route('/login')
def login():
    return render_template("index.html")

@frontendBP.route('/signup')
def signup():
    return render_template("index.html")

@frontendBP.route('/forgotPassword')
def forgotPassword():
    return render_template("index.html")

@frontendBP.route('/verifyEmail')
def verifyEmail():
    return render_template("index.html")

@frontendBP.route('/portal/files')
def files():
    return render_template("index.html")

@frontendBP.route('/portal/account')
def account():
    return render_template("index.html")

@frontendBP.route('/s')
def sharedFile():
    return render_template("index.html")