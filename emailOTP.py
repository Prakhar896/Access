from email import message
from main import *
import smtplib, ssl, re

def sendEmailWithOTP(destEmail, otp):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "noreply.accessportal@gmail.com"
    receiver_email = destEmail
    password = os.environ['AccessEmailPassword']
    message = """\
    Subject: OTP for Access Portal
    \n
    Your OTP is: {}
    """.format(otp)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

@app.route('/identity/createProcess/sendOTP', methods=['POST'])
def sendOTP():
    if 'Content-Type' not in request.headers:
        return "ERROR: Content-Type header not present in request. Request failed."
    if request.headers['Content-Type'] != 'application/json':
        return "ERROR: Content-Type header is not application/json. Request failed."
    if 'AccessAPIKey' not in request.headers:
        return "ERROR: AccessAPIKey header not present in request. Request failed."
    if request.headers['AccessAPIKey'] != os.environ['AccessAPIKey']:
        return "ERROR: AccessAPIKey header is not correct. Request failed."
    
    if 'email' not in request.json:
        return "ERROR: email field not present in request. Request failed."
    
    # Check if email field value is a valid email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", request.json['email']):
        return "ERROR: email field value is not a valid email. Request failed."
    
    email = request.json['email']

    numbers = [str(i) for i in range(10)]
    otp = ''.join(random.choice(numbers) for i in range(6))
    sendEmailWithOTP(email, otp)

    return "OTP sent to {}".format(email)
