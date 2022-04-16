# Access

**Q. What is Access?**

Access is many things. At its core, Access is a [Flask](https://flask.palletsprojects.com/en/1.1.x/) application that offers cloud storage services. Inspired by OneDrive, users of Access can create their own accounts and upload their own files to their respective Access folders in a very secure manner.

---

**Table Of Contents**

- [The Origins](#the-origins)
- [About The System](#about-the-system)
- [What This Means to Me](#what-this-means-to-me)
- [What Comes Next](#what-comes-next)

# The Origins

One day, I was going through the files I have stored on my OneDrive account and I realized that this simple cloud storage service is actually quite a marvelous feat. I wanted to make a mock-up cloud storage application of my own and hence I decided to make Access. I am a self-taught programmer and I have been learning Python and have built [Flask](https://flask.palletsprojects.com/en/2.1.x/) applications for the past few months.

# About The System

An Access Identity is known as the account that a user can create to navigate and access the various services Access has to offer. An Access Identity can be logged into with an email and a password.

I put security at the forefront of my design for the application. Around 1200 lines of code have been dedicated to ensure that every transaction on the site is secure and is authorised. Custom designed certificate generation, authentication token and API authorisation algorithms have been implemented in this web application to ensure the most secure experience.

![Sign In Screen](/docs/img/signinScreen.png)

> ABOVE: A screenshot of the login page of the system

Access is easily the biggest web server I have ever built; with Python as its backbone for the code, this web server has over 40 code files and nearly 4000 lines of code. The system in itself has 7+ sub-systems and services that aid the system administrator to fix any issues that arise in the system. The Access CheckUp Service, Access Analytics Recovery Mode and error-prevention measures worth more than 800 lines of code are just a few of them to name. 

The Access Analytics service also crunches data about the system's usage and generates savable usage reports for the administrator.

The entire system unanimously acts as a complete backend and frontend system. On the website itself, when the user logs in, the user is able to manage their account, upload/download/delete files from their Access Folder and more. The UI was designed with the help of [Bootstrap](https://getbootstrap.com). Login alerts, folder registration and identity creation emails are also sent to the user. At the moment, the system has been configured and hard-coded to allow only 3 file uploads per Access Identity.

<script src="http://code.jquery.com/jquery-1.4.2.min.js"></script> <script> var x = document.getElementsByClassName("site-footer-credits"); setTimeout(() => { x[0].remove(); }, 10); </script>