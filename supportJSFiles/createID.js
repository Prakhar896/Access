var username = ''
var pwd = ''
var email = ''

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
                    username = usernameField.value
                    password = passwordField.value
                    email = emailField.value
                    const otpEnteringSection = document.getElementById("otpEnteringSection")
                    otpEnteringSection.style.visibility = 'visible'
                    const accountDetailsSection = document.getElementById("accountDetailsSection")
                    accountDetailsSection.parentElement.removeChild(accountDetailsSection)
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

