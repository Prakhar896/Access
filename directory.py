from flask import Blueprint, request, send_file, send_from_directory, redirect, url_for
from models import Identity, File, AuditLog, EmailVerification
from decorators import jsonOnly, checkSession, enforceSchema, emailVerified, debug

directoryBP = Blueprint('directory', __name__)

a = Identity("john", "a@a.com", "1234", "today", None, {}, EmailVerification("abc", False), id="abc")

@directoryBP.route('/<path:filename>', methods=['POST'])
@checkSession(strict=True, provideIdentity=True)
@emailVerified
def uploadFile(user, filename):
    return "WIP"