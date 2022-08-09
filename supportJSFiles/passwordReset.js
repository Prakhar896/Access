
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

                            const sendOTPButton = document.getElementById("sendOTPButton")
                            sendOTPButton.parentNode.removeChild(sendOTPButton)

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
            alert("An error occurred in connecting to Access Servers. Please try again.")
        })
}