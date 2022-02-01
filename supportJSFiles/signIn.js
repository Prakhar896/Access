function signin() {
    const emailField = document.getElementById("emailField")
    const passwordField = document.getElementById("passwordField")
    const statusLabel = document.getElementById("statusLabel")

    if (!emailField.value || emailField.value == "" || !passwordField.value || passwordField.value == "") {
        alert("One or more fields is empty. Please try again.")
        return
    }

    statusLabel.style.visibility = 'visible'
    axios({
        method: 'post',
        url: `${origin}/api/loginIdentity`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            "email": emailField.value,
            "password": passwordField.value
        }
    })
    .then(response => {
        if (response.status == 200) {
            if (!response.data.userMessage) {
                if (!response.data.startsWith("ERROR:")) {
                    if (!response.data.startsWith("UERROR:")) {
                        if (response.data.startsWith("SUCCESS:")) {
                            const sessionData = response.data.substring("SUCCESS: Identity logged in. Auth Session Data: ".length)
                            const authToken = sessionData.split('-')[0]
                            const certID = sessionData.split('-')[1]
                            console.log("reached here")
                            statusLabel.innerHTML = "Logging you in..."
                            setTimeout(() => {
                                statusLabel.innerHTML = "Establishing secure connection..."
                            }, 1000)
                            setTimeout(() => {
                                statusLabel.innerHTML = "Logged in! Redirecting now..."
                                window.location = `${origin}/portal/session/${certID}/${authToken}/home`
                            }, 2000)
                        } else {
                            alert("An unknown response was received from Access Servers. This is likely an internal issue. Please try again. Check logs for more information.")
                            console.log('Unknown response received: ' + response.data)
                            statusLabel.style.visibility = 'hidden'
                        }
                    } else {
                        statusLabel.style.visibility = 'visible'
                        statusLabel.innerHTML = response.data.substring("UERROR: ".length)
                        console.log("User error occurred: " + response.data)
                    }
                } else {
                    alert("An error occurred in logging you in. Please try again. Check logs for more information.")
                    statusLabel.style.visibility = 'hidden'
                    console.log("Error occurred in making login request: " + response.data)
                }
            } else {
                statusLabel.style.visibility = 'visible'
                statusLabel.innerHTML = response.data.userMessage.substring("UERROR: ")
                console.log("There was an error from Certificate Authority on Access Servers: " + response.data.errorMessage)
                alert("There was an error in checking your Access Identity's certificate's security. Please try again or check logs for more information.")
            }
        } else {
            statusLabel.style.visibility = 'hidden'
            alert("There was an error in connecting to Access Servers. Please try again later.")
            console.log("Non-200 response status code received from Access Servers.")
        }
    })
    .catch(err => {
        console.log("An error occurred in connecting to Access Servers: " + err)
        alert("An error occurred in connecting to Access Servers. Please try again later or check logs for more information.")
        statusLabel.style.visibility = 'hidden'
    })
}