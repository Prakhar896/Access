from email import message
import smtplib, ssl, re, os, subprocess, sys, shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

class Emailer:
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    servicesEnabled = False
    sender_email = None
    password = None
    contextChecked = False

    @staticmethod
    def checkContext():
        if "EMAILING_ENABLED" in os.environ and os.environ['EMAILING_ENABLED'] == 'True':
            Emailer.sender_email = os.environ["SENDER_EMAIL"]
            Emailer.password = os.environ['SENDER_EMAIL_APP_PASSWORD']
            Emailer.servicesEnabled = True

        Emailer.contextChecked = True

    @staticmethod
    def sendEmail(destEmail, subject, altText, html):
        ## Email bypass
        if not Emailer.contextChecked:
            print("EMAILER Error: System context was not checked before sending email. Skipping email.")
            return True

        if not Emailer.servicesEnabled:
            print("EMAILER: Emailing services are not enabled. Skipping email.")
            return True
        
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