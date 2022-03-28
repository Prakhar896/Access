from email import message
import smtplib, ssl, re, os, subprocess, sys, shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

class Emailer:
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "noreply.accessportal@gmail.com"
    password = os.environ['AccessEmailPassword']

    @staticmethod
    def sendEmail(destEmail, subject, altText, html):
        ## Email bypass
        if 'GitpodEnvironment' in os.environ and os.environ['GitpodEnvironment'] == 'True':
            print("EMAILER: Skipping email due to Gitpod environment.")
            return
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = Emailer.sender_email
            message["To"] = destEmail

            part1 = MIMEText(altText, "plain")
            part2 = MIMEText(html, "html")

            message.attach(part1)
            message.attach(part2)

            context = ssl._create_unverified_context()
            with smtplib.SMTP_SSL(Emailer.smtp_server, Emailer.port, context=context) as server:
                server.login(Emailer.sender_email, Emailer.password)
                server.sendmail(Emailer.sender_email, destEmail, message.as_string())

            print("EMAILER: Email sent to {}".format(destEmail))
            return True
        except Exception as e:
            print("EMAILER ERROR: Failed to send email to {} with subject {}. Error: {}".format(destEmail, subject, e))
            return False