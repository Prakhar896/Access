from main import accessIdentities, validOTPCodes, fileUploadLimit, readableFileExtensions, CertAuthority, AFManager, AFMError, CAError, AccessAnalytics, Emailer, Encryption, Universal, Logger, obtainTargetIdentity, generateAuthToken
from flask import Flask, request, render_template, Blueprint, send_file, send_from_directory, url_for, redirect
import re, os, sys, json, random, copy, datetime, time

apiBP = Blueprint('api', __name__)

# Coming soon