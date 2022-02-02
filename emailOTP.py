from email import message
from main import *
import smtplib, ssl, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendEmailWithOTP(destEmail, otp):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "noreply.accessportal@gmail.com"
    receiver_email = destEmail
    password = os.environ['AccessEmailPassword']

    ## Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Access Portal OTP"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = """\
This is a message delivered by the Access Portal. Thank you for signing up for a new Access Identity. To finish up your sign-up process, enter the OTP (one-time password) below onto the website.


Your OTP is: {}

If you do not recognize this email, please ignore it.

THIS IS AN AUTOMATED MESSAGE FROM THE ACCESS PORTAL. DO NOT REPLY TO THIS MESSAGE.

Copyright 2022 Prakhar Trivedi.""".format(otp)

    html = render_template('emails/otpEmail.html', otpCode=otp)

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl._create_unverified_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

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

    validOTPCodes[email] = str(otp)
    json.dump(validOTPCodes, open('validOTPCodes.txt', 'w'))

    return "OTP sent to {}".format(email)
