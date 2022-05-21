// Fetch user's email preferences from servers
const statusLabel = document.getElementById("statusLabel")
const preferencesListingDiv = document.getElementById("preferencesListing")

statusLabel.style.visibility = 'visible';

var currentURL = document.URL
const userCertID = currentURL.split('/')[5]
var currentPreferencesState = {}

function updateUI(prefsData) {
    // Hide status label
    statusLabel.style.visibility = 'hidden'

    // Update current preferences state
    var data = prefsData
    if ("responseStatus" in data) {
        delete data["responseStatus"]
    }
    currentPreferencesState = data

    // Define HTML variables
    const checkedSwitchHTML = `
<div class="form-check form-switch">
    <input class="form-check-input" type="checkbox" role="switch" id="{{}}" checked onchange="updateAPI()">
    <label class="form-check-label" for="flexSwitchCheckChecked">{{}}</label>
</div>`
    const uncheckedSwitchHTML = `
<div class="form-check form-switch">
    <input class="form-check-input" type="checkbox" role="switch" id="{{}}" onchange="updateAPI()">
    <label class="form-check-label" for="flexSwitchCheckDefault">{{}}</label>
</div>`

    var listingDivHTML = ``

    for (var preference in data) {
        var readableText = ""
        if (preference == "fileDeletionNotifs") {
            readableText = "File Deletion Emails (Emails are sent whenever a file is deleted from your Access Folder)"
        } else if (preference == "fileUploadNotifs") {
            readableText = "File Upload Emails (Emails are sent whenever a file is uploaded to your Access Folder)"
        } else if (preference == "loginNotifs") {
            readableText = "Sign-in Emails (Emails for whenever you login to your Access Identity)"
        }
        if (data[preference] == true) {
            listingDivHTML += "\n<br>\n" + checkedSwitchHTML.replace("{{}}", preference).replace("{{}}", readableText)
        } else {
            listingDivHTML += "\n<br>\n" + uncheckedSwitchHTML.replace("{{}}", preference).replace("{{}}", readableText)
        }
    }

    // Finally, update div
    preferencesListingDiv.innerHTML = listingDivHTML
}

axios({
    method: 'post',
    url: `${origin}/api/userPreferences`,
    headers: {
        'Content-Type': 'application/json',
        'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
    },
    data: {
        'certID': userCertID,
        'resourceReq': 'emailPrefs'
    }
})
.then(response => {
    if (response.status == 200) {
        if (typeof response.data == "object") {
            if (response.data.responseStatus == "SUCCESS") {
                updateUI(response.data)
            } else {
                console.log(`A non-success response status with an object was received from Access Servers: ${response.data}`)
                alert("An error occurred in fetching your preferences' data. Please try again. Check logs for more information.")
                statusLabel.innerText = "An error occurred. Refresh this site."
            }
        } else if (typeof response.data == "string") {
            if (response.data.startsWith("ERROR")) {
                console.log("An error occurred in fetching preferences' data. Error response: " + response.data)
                alert("An error occurred in fetching your preferences' data. Please try again. Check logs for more information.")
                statusLabel.innerText = "An error occurred. Refresh this site."
            } else {
                console.log("An unknown response string was received from Access Servers. Response: " + response.data)
                alert("An unknown response string was received from Access Servers. Please try again. Check logs for more information.")
                statusLabel.innerText = "An error occurred. Refresh this site."
            }
        } else {
            console.log("An unknown response was received from Access Servers. Response: " + response.data)
            alert("An unknown response was received from Access Servers. Please try again. Check logs for more information.")
            statusLabel.innerText = "An error occurred. Refresh this site."
        }
    } else {
        console.log("Non-200 status code response was received from Access Servers. Response data: " + response.data)
        alert("Failed to connect to Access Servers. Please try again. Check logs for more information.")
        statusLabel.innerText = "An error occurred. Refresh this site."
    }
})
.catch(error => {
    console.log("An error occurred in connecting to Access Servers. Error: " + error)
    alert("An error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
    statusLabel.innerText = "An error occurred. Refresh this site."
})

function updateAPI() {
    var updatedSwitchID = ''
    var updatedSwitchNewStatus = false
    for (var preference in currentPreferencesState) {
        const targetSwitch = document.getElementById(preference)
        if (targetSwitch.checked != currentPreferencesState[preference]) {
            updatedSwitchID = preference
            updatedSwitchNewStatus = targetSwitch.checked
        }
    }

    // Send user preference update request to API

}