<img src="https://github.com/Prakhar896/Access/blob/revamp/assets/logo/png/logo-color.png?raw=true" alt="Access Logo" height="150px">

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Firebase](https://img.shields.io/badge/firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Chakra UI](https://img.shields.io/badge/Chakra--UI-319795?style=for-the-badge&logo=chakra-ui&logoColor=white)
![Axios](https://img.shields.io/badge/axios-671ddf?&style=for-the-badge&logo=axios&logoColor=white)

# Access

<img src="img/accessHome.png" alt="Screenshot of the Access dashboard. A website with a white background is displayed, with a black and white 'Access' logo at the top-left in monospace font. Below the logo is the heading, 'My Files'. Far right of the heading is an upload icon, indicating the button to trigger the upload popover. In the centre, a table lists all of the user's uploaded files, with last modified and uploaded date information. The table lists just one file, 'MyFile.pdf', and there's a menu button in the 'Actions' column" height="300px">

**Access is a simple, easy-to-use cloud file storage system with neat features like file sharing and sorting. 🙌🤩** It is the perfect tool for quick, efficient and hassle free online file storage. ✨

Access is a Python Flask web server that renders a Vite-built React frontend designed with Chakra UI. The system can also use Firebase Realtime Database to act as a robust cloud database system. Incorporating a variety of complex logic, services and integrations, Access delivers a clean and smooth user experience for users. 🚀🤯

Hopefully, the system is live at: [https://access.prakhar.app](https://access.prakhar.app) ! 🎉

[Check out the GitHub here! ✨](https://github.com/Prakhar896/Access)

## Show Don't Tell

<img src="img/accessHome.png" alt="Screenshot of the Access dashboard. A website with a white background is displayed, with a black and white 'Access' logo at the top-left in monospace font. Below the logo is the heading, 'My Files'. Far right of the heading is an upload icon, indicating the button to trigger the upload popover. In the centre, a table lists all of the user's uploaded files, with last modified and uploaded date information. The table lists just one file, 'MyFile.pdf', and there's a menu button in the 'Actions' column." height="300px">

**Dashboard**

Access' dashboard is a clean, minimalistic and easy-to-use interface that allows users to upload, download, share and manage their files. The dashboard is designed to be user-friendly and intuitive, making it easy for users to navigate and use the system. 📁📂

File actions are neatly obscured behind a menu button next to the filename, while other key actions like logout are neatly presented at the top.

The entire user experience was also designed to be responsive, adapting well to smaller screen formats. 📱

---

<img src="img/sorting.png" alt="A zoomed in screenshot on the popover that appears after clicking the 'Sort by' button next to the 'My Files' heading on the Access Dashboard. The popover consists of two sections, 'Attribute', which lists the available sorting attributes 'Name', 'Last Modified', and 'Uploaded'. The second section, titled 'Order', lists 'Ascending' and 'Descending' as available orders. Currently, 'Last Modified' and 'Descending' are checked, indicating that the sorting order is descending of a file's last modified date." height="300px">

**Sorting**

Keeping track of files can get messy; so Access allows users to quickly sort their files by various attributes in ascending/descending order. The system also remembers the user's preference, so sorting is always consistent. 📝🔍

---

<img src="img/rename.png" alt="Screenshot of a popover titled 'Rename File'. The popover prompts the user to enter the new file name for 'MyFile.pdf' with a text field. A black and white 'Rename' button in black and white is placed bottom-right." height="300px">

**Menu Actions**

Expected file actions like seeing last modified and uploaded date information, renaming and deleting files are neatly tucked behind a menu button. All the complex functionality is obscured behind neat modals that popover the screen to bring their attention to the task at hand. 📋🗑️

---

**Sharing**

<img src="img/noSharing.png" alt="Screenshot of a popover titled 'Sharing'. Under a text 'Sharing Active', 'No' is written in bold red. Below this, a section titled 'Start Sharing' is shown, with the description 'Create a public link that can be used by anyone to access this file. Optionally, password protect it.' A text field labelled 'Password (Optional)' is below this description. A black and white 'Start Sharing' button is placed bottom-right." height="300px">

Users often want to share important files with others. Access allows this through public links that can be tightly controlled by the user. Users can even password protect links, so that only those with the password can access the file. 🔒🔗

<img src="img/sharingActive.png" alt="Screenshot of a popover titled 'Sharing'. Under a text 'Sharing Active', 'Yes' is written in bold green, followed by a public link ID for the file. Under the text 'Share Link', a black and white button 'Copy Share Link' is present. Under 'Password Required', 'Yes' is written in bold black. Under 'File name', 'MyFile.pdf' is in bold black. Under 'Downloads', '0' is in bold black. A few buttons that can be used to manage the file sharing are placed bottom-right. A button with outline and font color in red with a white background labelled 'Deactivate' is placed second to bottom right. On the right of this, a button with a solid red background and white font color labelled 'Stop Sharing' sits bottom right." height="300px">

After starting sharing for a file, users can quickly copy the public link and start distributing. Access will also collect download metrics to help users understand how their files are being accessed. 📊📈

Sharing links can be deactivated and deleted ("Stop Sharing") anytime. 🛑

<img src="img/sharedFile.png" alt="Screenshot of the Access Shared File page. Under the Access logo, which, in white monospace font against a black background, says 'Access', a heading 'Shared File' is written. Below, 'prakhar is sharing MyFile.pdf with you' is written to indicate the file share's details. Below, in bold, a text reads 'This file is password protected.' Below, a textfield labelled 'Enter password' is seeking user input. Below, a button with solid black background and white font color labelled 'Access' is placed." height="300px">

Public accessors can see this when trying to use a public file share link. Password protected files will require accessors to enter the password before downloading the file. 🔑

If all is right, hitting "Access" will start the download. 📥

---

<img src="img/myAccount.png" alt="Screenshot of the 'My Account' dashboard for Access users. Top-left, below the Access logo, a title reads 'My Account'. On the right of the heading, a black background with white font color button reads 'Manage Password'. Next to this, a button in solid green with a save-indicating icon is placed. Below, on the left, textfields for 'Username' and 'Email' are provided to update user information. Below this, still on the left, user information is provided under 'Last login' and 'Created on' texts. The last element, still on the left half, is a button in red outline and font color with a white background which reads 'Delete Identity'. On the right half, a grey-background container is positioned with the title 'Audit Logs'. Several audit logs, each of which include the event (e.g 'FILEUPLOAD'), date and description of the log, are listed under this title. Most logs are behind a scroll, while the top four can be seen." height="300px">

**My Account**

Managing user information is super easy and intuitive in Access. In the My Account dashboard, which can be accessed through the sidebar on the left, users can update their username, email, and password. They can also see their last login and account creation date information. 📝🔒

All actions, like file uploads, email verification, renames, overwrites and more, are all attached to accounts as audit logs. These logs can be seen in the Audit Logs section for the user to trace changes. 📜

## Background

<img src="img/oldAccess.png" alt="Screenshot of an older version of Access. In the centre of a page with a white background, at the top, a logo in old-school boxy font reads 'ACCESS'. Below, in the same image and in cursive font, a text reads 'We keep your world secure'. Below, a heading in Times New Roman reads 'Welcome to Access!'. Below, a description reads 'This is a service to access sensitive information in a safe and secure manner.' Below, a text reads 'Please select an option below to gain access to your Access Folder:'. Two buttons in dark green solid background with white font color are placed vertically, labelled 'Create an Access Identity' and 'Sign in to an Access Identity' respectively. Finally, a small text reads '© 2022 Prakhar Trivedi'." height="300px">

In early 2022, I was facing issues with cloud storage solutions like OneDrive and Google Drive. Around the same time, I was learning about Python and Flask, and I decided that, I could just build my own cloud storage system instead! Excited to apply the skills I was learning, I dived right in.

Of course, being still a novice to Python, Flask and web server programming, the code I wrote was not very good and had many issued throughout. I released updates that slowly fixed some of these pitfalls, but the UX was sitll very slow and unappealing. 2 years and the equipping of many new skills later, I decided to completely destroy and revamp Access from the ground up in a `2.0` update.

## Access 2.0

Access 2.0 is a complete revamp of the original Access System. A quick comparison:

| Old Architecture | New Architecture |
|------------------|------------------|
| Entire JSON database stored in-memory in one variable. No scalability, no failover. | Use Firebase Realtime Database as cloud database which is good way to backup data. |
| Difficult to update database. Saving just one attribute update would mean dumping the whole database entirely to data file. | Custom database management system which incorporates failover-to-local-database. De-sync state handling. Referential data management for efficiency. Abstract base data model defining expectations for real data models for structured data definition. |
| No concurrency. | Incorporate concurrency for tasks that require more time like dispatching emails or saving files so that main worker is not held up. |
| Slow and unappealing UI. | Use React to design frontend and incorporate framer-motion library to create animations. |

The new Access is designed to be more robust, efficient and user-friendly. It incorporates a variety of new features and improvements that make it a much better system than the original. 🚀🤯

Access 1.x users, I highly recommend upgrading to the new Access system, but unfortunately, due to the entirely new architecture, I could not implement automatic backwards compatibility. Please taking note that existing Access 1.x data files and databases are not compatible with Access 2.0 before updating!

It is recommended to use the [new updater script](https://github.com/Prakhar896/Access/blob/6350875ff26442a5c268be4479a3347c8b31a499/updater.py) to update to Access 2.x, as it supports the new architecture.

---

Thanks for checking out Access, have a great day! 🎉🚀

© 2022-2024 Prakhar Trivedi. All rights reserved.

<script src="http://code.jquery.com/jquery-1.4.2.min.js"></script> <script> var x = document.getElementsByClassName("site-footer-credits"); setTimeout(() => { x[0].remove(); }, 10); </script>
