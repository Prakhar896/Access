const statusLabel = document.getElementById("statusLabel")

function updatePassword() {
    const currentPasswordField = document.getElementById("currentPasswordField")
    const newPasswordField = document.getElementById("newPasswordField")
    const confirmPasswordField = document.getElementById("confirmPasswordField")

    if (!currentPasswordField.value || currentPasswordField.value == "" || !newPasswordField.value || newPasswordField.value == "" || !confirmPasswordField.value || confirmPasswordField.value == "") {
        alert("One or more fields are empty. Please try again.")
        return
    }

    if (newPasswordField.value != confirmPasswordField.value) {
        statusLabel.style.visibility = 'visible'
        statusLabel.innerText = "New Password and Confirm Password fields do not match. Try again."
        return
    }

    statusLabel.style.visibility = 'visible'
    statusLabel.innerText = 'Processing...'

    var certID = document.URL.split('/')[5]

    axios({
        method: 'post',
        url: `${location.origin}/api/updateIdentityPassword`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            'certID': certID,
            'currentPass': currentPasswordField.value,
            'newPass': newPasswordField.value
        }
    })
        .then(response => {
            if (response.status == 200) {
                if (!response.data.startsWith("UERROR")) {
                    if (!response.data.startsWith("ERROR")) {
                        if (response.data.startsWith("SUCCESS")) {
                            statusLabel.innerText = "Password successfully updated. Redirecting back..."

                            setTimeout(() => {
                                document.getElementById("backToPortalActualButton").click()
                            }, 3000)
                        } else {
                            alert("An unknown string response was received from Access Servers. Please try again. Check logs for more information.")
                            console.log("Unknown response string received when updating password: " + response.data)
                            statusLabel.style.visibility = 'hidden'
                        }
                    } else {
                        alert("An error occurred in updating your password. Please try again. Check logs for more information.")
                        console.log("Error occurred in updating password: " + response.data)
                        statusLabel.style.visibility = 'hidden'
                    }
                } else {
                    statusLabel.style.visibility = 'visible'
                    statusLabel.innerText = response.data.substring("UERROR: ".length)
                }
            } else {
                alert("Failed to connect to Access Servers. Please try again. Check logs for more information.")
                console.log("Non-200 status code response received from Access Servers: " + response.data)
                statusLabel.style.visibility = 'hidden'
            }
        })
        .catch(error => {
            alert("An error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
            console.log("Error in connecting to Access Servers: " + error)
            statusLabel.style.visibility = 'hidden'
        })
}

document.getElementById("confirmPasswordField")
    .addEventListener("keyup", (event) => {
        event.preventDefault()
        if (event.keyCode === 13) {
            document.getElementById("updatePasswordButton").click();
        }
    })