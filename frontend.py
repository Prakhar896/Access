from flask import Flask, Blueprint, redirect, render_template, request, url_for

frontendBP = Blueprint('frontend', __name__)

@frontendBP.route('/')
def homepage():
    return render_template("index.html")

@frontendBP.route('/s')
def sharedFile():
    return render_template("index.html")