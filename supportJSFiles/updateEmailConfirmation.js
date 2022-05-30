const statusLabel = document.getElementById("statusLabel")

function sendOTPVerification() {
    const newEmailField = document.getElementById("newEmail")
    const currentPasswordField = document.getElementById("currentPasswordField")

    if (newEmailField.value == "" || !newEmailField.value || currentPasswordField.value == "" || !currentPasswordField.value) {
        alert("One or more fields is empty. Please try again.")
        return
    }

    var certID = document.URL.split('/')[5]

    statusLabel.innerText = "Processing..."
    statusLabel.style.visibility = "visible";

    axios({
        method: 'post',
        url: `${location.origin}/api/confirmEmailUpdate`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            'certID': certID,
            'currentPass': currentPasswordField.value,
            'newEmail': newEmailField.value
        }
    })
        .then(response => {
            if (response.status == 200) {
                if (!response.data.startsWith("UERROR")) {
                    if (!response.data.startsWith("ERROR")) {
                        if (response.data.startsWith("SUCCESS")) {
                            // SUCCESS CASE
                            const otpEnteringSection = document.getElementById("otpEnteringSection")
                            otpEnteringSection.style.visibility = "visible";

                            var sendOTPButton = document.getElementById("sendOTPButton")
                            sendOTPButton.parentElement.removeChild(sendOTPButton)

                            // disable interaction with other fields
                            var noInteracts = document.getElementsByClassName('toDisableFields');
                            [].map.call(noInteracts, function (elem) {
                                elem.addEventListener("keydown", function (e) {
                                    if (e.keyCode != 9) {
                                        e.returnValue = false;
                                        return false;
                                    }
                                }, true);
                            });

                            statusLabel.style.visibility = 'hidden';
                            document.getElementById("backToPortalButton").style.visibility = 'hidden';
                            alert("An email with an OTP code was sent to your new email. Please enter that code here to verify your new email.")
                        } else {
                            alert("An unknown string response was received from Access Servers. Please try again. Check logs for more information.")
                            console.log("Unknown response received: " + response.data)
                            statusLabel.style.visibility = 'hidden'
                        }
                    } else {
                        alert("An error occurred in sending confirmation email to your new email. Please try again. Check logs for more information.")
                        console.log("Error occurred in sending confirmation email: " + response.data)
                        statusLabel.style.visibility = 'hidden'
                    }
                } else {
                    statusLabel.innerText = response.data.substring("UERROR: ".length)
                    console.log("User error occurred in sending confirmation email: " + response.data)
                }
            } else {
                alert("There was an error in connecting to Access Servers. Please try again. Check logs for more information.")
                console.log("Non-200 status code response was received from Access Servers. Response data: " + response.data)
                statusLabel.style.visibility = 'hidden'
            }
        })
        .catch(error => {
            alert("An error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
            console.log("Error in connecting to Access Servers: " + error)
            statusLabel.style.visibility = 'hidden'
        })
}

function updateEmail() {
    const newEmailField = document.getElementById("newEmail")
    const currentPasswordField = document.getElementById("currentPasswordField")
    const otpCodeField = document.getElementById("otpField")

    if (newEmailField.value == "" || !newEmailField.value || currentPasswordField.value == "" || !currentPasswordField.value || !otpCodeField.value || otpCodeField.value == "") {
        alert("One or more fields is empty. Please try again.")
        return
    }

    var certID = document.URL.split('/')[5]

    statusLabel.innerText = "Processing..."
    statusLabel.style.visibility = "visible";

    axios({
        method: 'post',
        url: `${origin}/api/updateIdentityEmail`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            'certID': certID,
            'currentPass': currentPasswordField.value,
            'newEmail': newEmailField.value,
            'otpCode': otpCodeField.value
        }
    })
        .then(response => {
            if (response.status == 200) {
                if (!response.data.startsWith("UERROR")) {
                    if (!response.data.startsWith("ERROR")) {
                        if (response.data.startsWith("SUCCESS")) {
                            statusLabel.innerText = "Email successfully updated! Re-directing back now..."

                            setTimeout(() => {
                                document.getElementById("backToPortalActualButton").click()
                            }, 3000)
                        } else {
                            alert("An unknown string response was received from Access Servers. Please try again. Check logs for more information.")
                            console.log("Unknown response: " + response.data)
                            statusLabel.style.visibility = 'hidden'
                        }
                    } else {
                        alert("An error occurred when updating the email. Please try again. Check logs for more information.")
                        console.log("Error occurred in updating identity email: " + response.data)
                        statusLabel.style.visibility = 'hidden'
                    }
                } else {
                    statusLabel.innerText = response.data.substring("UERROR: ".length)
                    console.log("User error occurred in updating identity email: " + response.data)
                }
            } else {
                alert("Failed to connect to Access Servers. Please try again. Check logs for more information.")
                console.log("Non-200 status code response received from Access Servers: " + response.data)
                statusLabel.style.visibility = 'hidden'
            }
        })
        .catch(error => {
            alert("An error occurred in connecting to Access servers. Please try again. Check logs for more information.")
            console.log("Error in connecting to Access Servers: " + response.data)
            statusLabel.style.visibility = 'hidden'
        })
}

document.getElementById("newEmail")
    .addEventListener("keyup", (event) => {
        event.preventDefault()
        if (event.keyCode === 13) {
            document.getElementById("sendOTPButton").click();
        }
    })

document.getElementById("otpField")
    .addEventListener("keyup", (event) => {
        event.preventDefault()
        if (event.keyCode === 13) {
            document.getElementById("updateEmailButton").click();
        }
    })