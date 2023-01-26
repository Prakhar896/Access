function sendOTP() {
    const statusLabel = document.getElementById("statusLabel")
    const usernameField = document.getElementById("usernameField")
    const emailField = document.getElementById("emailField")
    const passwordField = document.getElementById("passwordField")

    if (!usernameField.value || usernameField.value == "" || !emailField.value || emailField.value == "" || !passwordField.value || passwordField.value == "") {
        alert("One or more fields are empty. Please try again.")
        return
    }
    statusLabel.style.visibility = 'visible'
    axios({
        method: 'post',
        url: `${origin}/identity/createProcess/sendOTP`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            "email": emailField.value
        }
    })
    .then(response => {
        statusLabel.style.visibility = 'hidden'
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR")) {
                if (response.data == `OTP sent to ${emailField.value}`) {
                    alert("An OTP code was sent to your inbox. To finish signing up, please verify yourself by entering the code sent to you.")
                    const otpEnteringSection = document.getElementById("otpEnteringSection")
                    otpEnteringSection.style.visibility = 'visible'
                    const accountDetailsSection = document.getElementById("accountDetailsSection")
                    accountDetailsSection.removeChild(document.getElementById("createIDButton"))
                    accountDetailsSection.parentElement.removeChild(document.getElementById("information"))
                } else {
                    alert("An unknown non-error response was received from Access Servers. Please try again later. See console for more information.")
                    console.log("Unknown non-error response received: " + response.data)
                }
            } else {
                console.log(response.data)
                alert("An error was received from Access Servers. Please try again. Check logs for more information.")
            }
        } else {
            console.log("Non-200 status code received in response. Response data: " + response.data)
            alert("There was an error in successfully connecting to Access Servers. Please try again. Check logs for more information.")
        }
    })
    .catch(err => {
        statusLabel.style.visibility = 'hidden'
        console.log(`Error: ${err}`)
        alert("An error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
    })
}

function makeIdentity() {
    const statusLabel = document.getElementById("statusLabel")
    const usernameField = document.getElementById("usernameField")
    const emailField = document.getElementById("emailField")
    const passwordField = document.getElementById("passwordField")
    const otpCodeField = document.getElementById("otpField")


    if (!usernameField.value || usernameField.value == "" || !emailField.value || emailField.value == "" || !passwordField.value || passwordField.value == "") {
        alert("One or more account details fields are empty. Please try again.")
        return
    }
    if (!otpCodeField.value || otpCodeField.value == "") {
        alert("OTP Code field is empty. Please enter your OTP code and try again.")
        return
    }

    statusLabel.style.visibility = 'visible'
    axios({
        method: 'post',
        url: `${origin}/api/createIdentity`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            "username": usernameField.value,
            "password": passwordField.value,
            "email": emailField.value,
            "otpCode": otpCodeField.value
        }
    })
    .then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR")) {
                if (!response.data.startsWith("UERROR")) {
                    if (response.data == "SUCCESS: Identity created.") {
                        statusLabel.innerHTML = "Creating Identity..."
                        setTimeout(() => {
                            statusLabel.innerHTML = "Identity created! Redirecting to login site..."
                            location = `${origin}/identity/login/?email=${emailField.value}`
                        }, 2000)
                    } else {
                        statusLabel.style.visibility = 'hidden'
                        alert("An unknown error occurred in creating the identity. Please try again. Check logs for more information.")
                        console.log("Unrecognised response: " + response.data)
                    }
                } else {
                    statusLabel.style.visibility = 'visible'
                    statusLabel.innerHTML = `Error: ${response.data.substring("UERROR: ".length)}`
                    console.log("User error occurred: " + response.data)
                }
            } else {
                statusLabel.style.visibility = 'hidden'
                alert("An internal error occurred in creating the identity. Please try again. Check logs for more information.")
                console.log("Internal error: " + response.data)
            }
        } else {
            statusLabel.style.visibility = 'hidden'
            alert("An unknown error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
            console.log("Non-200 status code response received from access servers.")
        }
    })
    .catch(err => {
        statusLabel.style.visibility = 'hidden'
        alert("An error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
        console.log("Error occurred in connecting to Access: " + err)
    })
}