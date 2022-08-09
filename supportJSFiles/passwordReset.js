
function sendPwdResetKey() {
    const statusLabel = document.getElementById("statusLabel")
    const identityEmailFieldDiv = document.getElementById("identityEmailFieldDiv")
    const newPasswordEnteringSection = document.getElementById("newPasswordEnteringSection")
    const identityEmailField = document.getElementById("identityEmailField")

    if (!identityEmailField.value || identityEmailField.value == "") {
        alert("One or more fields are empty. Please try again.")
        return
    }

    statusLabel.style.visibility = 'visible'
    statusLabel.innerText = 'Processing...'

    axios({
        method: 'post',
        url: `${origin}/api/sendResetKey`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            'identityEmail': identityEmailField.value
        }
    })
        .then(response => {
            if (response.status == 200) {
                if (!response.data.startsWith("UERROR")) {
                    if (!response.data.startsWith("ERROR")) {
                        if (response.data == "SUCCESS: Reset key was successfully sent to the identity's email.") {
                            // SUCCESS Case
                            statusLabel.style.visibility = 'hidden'

                            const sendResetKeyButton = document.getElementById("sendResetKeyButton")
                            sendResetKeyButton.parentElement.removeChild(sendResetKeyButton)
                            const backToPortalButton = document.getElementById("backToPortalButton")
                            backToPortalButton.parentElement.removeChild(backToPortalButton)

                            newPasswordEnteringSection.style.visibility = 'visible'

                            // disable interaction
                            var noInteracts = document.getElementsByClassName('toDisableFields');
                            [].map.call(noInteracts, function (elem) {
                                elem.addEventListener("keydown", function (e) {
                                    if (e.keyCode != 9) {
                                        e.returnValue = false;
                                        return false;
                                    }
                                }, true);
                            });

                        } else {
                            statusLabel.style.visibility = 'hidden'
                            console.log("Unknown response received from Access Servers when sending password reset key: " + response.data)
                            alert("An unknown response was received from Access Servers when trying to send password reset key. Check logs for more information.")
                        }
                    } else {
                        statusLabel.style.visibility = 'hidden'
                        console.log("Error response received from Access Servers when sending password reset key: " + response.data)
                        alert("An error occurred in sending the password reset key. Check logs for more information.")
                    }
                } else {
                    statusLabel.style.visibility = 'visible'
                    statusLabel.innerText = response.data.substring("U".length)
                    console.log("User error occurred while sending password reset key: " + response.data)
                }
            } else {
                statusLabel.style.visibility = 'hidden'
                console.log("Non-200 status code response received from Access Servers while sending password reset key.")
                alert("An error occurred in connecting to Access Servers. Please try again.")
            }
        })
        .catch(error => {
            statusLabel.style.visibility = 'hidden'
            console.log("Error occurred in connecting to Access Servers while sending password reset key: " + error)
            alert("An error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
        })
}

function resetPassword() {
    const statusLabel = document.getElementById("statusLabel")
    const identityEmailFieldDiv = document.getElementById("identityEmailFieldDiv")
    const newPasswordEnteringSection = document.getElementById("newPasswordEnteringSection")

    const identityEmailField = document.getElementById("identityEmailField")
    const resetKeyField = document.getElementById("resetKeyField")
    const newPasswordField = document.getElementById("newPasswordField")
    const confirmNewPasswordField = document.getElementById("confirmNewPasswordField")

    if (!identityEmailField.value || identityEmailField.value == "" || !resetKeyField.value || resetKeyField.value == "" || !newPasswordField.value || newPasswordField.value == "" || !confirmNewPasswordField.value || confirmNewPasswordField.value == "") {
        alert("One or more fields are empty. Please try again.")
        return
    }

    statusLabel.style.visibility = 'visible'
    statusLabel.innerText = "Processing..."

    if (newPasswordField.value != confirmNewPasswordField.value) {
        statusLabel.innerText = "New password and confirm password fields do not match."
        return
    }

    axios({
        method: 'post',
        url: `${origin}/api/resetPassword`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            'identityEmail': identityEmailField.value,
            'resetKey': resetKeyField.value,
            'newPassword': newPasswordField.value
        }
    })
        .then(response => {
            if (response.status == 200) {
                if (response.data != "UERROR: No reset key was sent to this identity. If you did get a reset key email, the key may have expired if you are entering it more than 15 minutes after the reset key email was sent to you.") {
                    if (!response.data.startsWith("UERROR")) {
                        if (!response.data.startsWith("ERROR")) {
                            if (response.data.startsWith("SUCCESS")) {
                                statusLabel.style.visibility = 'visible'
                                statusLabel.innerText = "Password reset successful! Re-directing to login page..."

                                setTimeout(() => {
                                    location.href = `${origin}/identity/login?email=${identityEmailField.value}`
                                }, 2000)
                            }
                        } else {
                            statusLabel.style.visibility = 'hidden'
                            console.log("Error occurred in resetting password: " + response.data)
                            alert("An error occurred in resetting the password. Check logs for more information.")
                        }
                    } else {
                        statusLabel.style.visibility = 'visible'
                        statusLabel.innerText = response.data.substring("UERROR: ".length)
                        console.log("User error occurred in resetting password: " + response.data)
                    }
                } else {
                    statusLabel.style.visibility = 'visible'
                    statusLabel.innerText = response.data.substring("UERROR: ".length)
                    console.log("User error occurred in resetting password: " + response.data)

                    const requestNewButton = document.getElementById("requestNewKeyButton")
                    requestNewButton.style.visibility = 'visible'
                    alert("Reset key is incorrect. If you are certain that you entered the exact key from the email that was sent and think that the key expired, click the 'Request New Key' button at the bottom.")
                }
            } else {
                statusLabel.style.visibility = 'hidden'
                console.log("Non-200 status code response received from Access Servers while resetting password.")
                alert("An error occurred in connecting to Access Servers. Please try again.")
            }
        })
        .catch(error => {
            statusLabel.style.visibility = 'hidden'
            console.log("Error occurred in connecting to Access Servers: " + error)
            alert("An error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
        })
}

function requestNewKey() {
    location.reload()
}

document.getElementById("identityEmailField")
    .addEventListener("keyup", (event) => {
        event.preventDefault()
        if (event.keyCode === 13) {
            document.getElementById("sendResetKeyButton").click();
        }
    })

document.getElementById("confirmNewPasswordField")
    .addEventListener("keyup", (event) => {
        event.preventDefault()
        if (event.keyCode === 13) {
            document.getElementById("resetPasswordButton").click();
        }
    })