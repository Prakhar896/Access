<img src="https://github.com/Prakhar896/Access/blob/revamp/assets/logo/png/logo-color.png?raw=true" alt="Access Logo" height="150px">

# Setup Guide

Access' inner workings are rather unique and fluid. Multiple sub-systems and components work in efficient harmony to deliver a great user experience. Access is highly clone-friendly, and can be easily set up by yourself.

## Pre-requisites

- [Python 3.11](https://www.python.org/downloads)
- [Git](https://git-scm.com/downloads)

If you are looking to enable emailing services, you will need a Google Account to which Access can connect to for SMTP-based email dispatch. For authorisation, [App Passwords](https://support.google.com/accounts/answer/185833?hl=en#zippy=%2Cwhy-you-may-need-an-app-password%2Capp-passwords-revoked-after-password-change) are used. Steps:
1. Create a Google Account if you don't have one.
2. Enable 2FA on the Google Account, if not already enabled.
3. Go to the [MyAccount dashboard](https://myaccount.google.com)
4. Go to Security > [App Passwords](https://myaccount.google.com/apppasswords)
5. Give your new app password a name and generate it. Store the password in a safe place. The spaces don't matter, and you should just remove them to form one string.

If you are looking to enable the Firebase Realtime Database syncing, follow these steps to get your Firebase project ready:
1. Visit the [Firebase Console](https://console.firebase.google.com)
2. Create a new project
3. Go to Project Overview > Project Settings > Service accounts and click "Generate new private key". The key should be downloaded as a JSON file to your computer.
4. Rename the JSON file to `serviceAccountKey.json`

## Installing Access

### Downloading source code

There's a few ways to do this. You can either visit the [source code releases](https://github.com/Prakhar896/Access/releases) and download the zip package of your intended version, or you can clone the repository using Git.

If cloning, here's the Git command:
```zsh
git clone https://github.com/Prakhar896/Access
```

Either way, be aware of where you're cloning/downloading the source code. This will be important in the following steps.

### Setting up the environment

1. Open a terminal and navigate to the root directory of the source code.
2. If you wish, [create a virtual environment](https://docs.python.org/3/library/venv.html) for the project and activate it. This is optional but recommended.
3. Install the required dependencies using pip:
```zsh
pip install -r requirements.txt
```
4. If you wish to enable Firebase Realtime Database syncing, place the `serviceAccountKey.json` file in the root directory of the source code.
5. Create a `.env` file in the root directory. Various components of the system can be configured through this file. Here's a guide:
```env
RuntimePort= # required, port on which the system will run.
SYSTEM_URL= # required, URL of the system used in emails. for local development, use http://localhost:<RuntimePort>
APP_SECRET_KEY= # required, used to encrypt user sessions. any string will do.
APIKey= # required, API key for request authorisation. any string will do.
LOGGING_ENABLED= # required, set to True to enable logging.
AccessAnalyticsEnabled= # required, set to True to enable Access Analytics.
EMAILING_ENABLED= # required, set to True to enable emailing services.
FireConnEnabled= # required, set to True to enable connections with Firebase
FireRTDBEnabled= # required, set to True to enable database syncing with a Firebase Realtime Database. requires FireConnEnabled to be True, if enabled.
RTDB_URL= # optional, required if FireRTDBEnabled is True. this is the URL of the Firebase Realtime Database.
SENDER_EMAIL= # optional, required if EMAILING_ENABLED is True. this is the email of the Google Account through which SMTP emails will be sent.
SENDER_EMAIL_APP_PASSWORD= # optional, required if EMAILING_ENABLED is True. this is the app password of the Google Account through which SMTP emails will be sent.
CLEANER_DISABLED= # optional, set to True to disable the cleaner agent. the cleaner agent helps to clean up unverified accounts every 3 hours.
DEBUG_MODE= # optional, set to True to enable debug mode. this will enable debug messages and stack traces in the console.
DECORATOR_DEBUG_MODE= # optional, set to True to see debug messages from requests processed by decorators
```