import os, sys, datetime, copy
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

adminBP = Blueprint('admin', __name__)

@adminBP.route('/admin')
def adminHome():
    return "<h1>Hello, this is the Admin Domain</h1>"