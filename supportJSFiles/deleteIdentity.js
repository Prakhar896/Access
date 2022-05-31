const statusLabel = document.getElementById("statusLabel")

function deleteConfirmed() {
    const currentPasswordField = document.getElementById("currentPasswordField")

    if (!currentPasswordField.value || currentPasswordField.value == "") {
        alert("One or more fields are empty. Please try again.")
        return
    }

    statusLabel.style.visibility = 'visible'
    statusLabel.innerText = 'Processing, this may take a second...'

    var certID = document.URL.split('/')[5]
    var authToken = document.URL.split('/')[6]

    axios({
        method: 'post',
        url: `${origin}/api/deleteIdentity`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            'certID': certID,
            'currentPass': currentPasswordField.value,
            'authToken': authToken
        }
    })
        .then(response => {
            if (response.status == 200) {
                if (!response.data.startsWith("UERROR")) {
                    if (!response.data.startsWith("ERROR")) {
                        if (!response.data.startsWith("SYSTEMERROR")) {
                            if (response.data.startsWith("SUCCESS")) {
                                statusLabel.innerText = "Almost done..."

                                setTimeout(() => {
                                    statusLabel.innerText = "Access Identity was successfully deleted! Re-directing back to Access Home..."
                                }, 3000)

                                setTimeout(() => {
                                    window.location = origin
                                }, 5000)
                            } else {
                                alert("Unknown string response received from Access Servers. Please try again. Check logs for more information.")
                                console.log("Unknown string response received: " + response.data)
                                statusLabel.style.visibility = 'hidden'
                            }
                        } else {
                            alert("A server-side error occurred in deleting your identity. Please try again. Check logs for more information.")
                            console.log("Server-side system error occurred in deleting identity: " + response.data)
                            statusLabel.style.visibility = 'hidden'
                        }
                    } else {
                        alert("An error occurred in deleting your identity. Please try again. Check logs for more information.")
                        console.log("Error occurred in deleting identity: " + response.data)
                        statusLabel.style.visibility = 'hidden'
                    }
                } else {
                    statusLabel.innerText = response.data.substring("UERROR: ".length)
                    statusLabel.style.visibility = 'visible'
                }
            } else {
                alert("Failed to connect to Access Servers. Please try again. Check logs for more information.")
                console.log("Non-200 status code response received from Access Servers: " + response.data)
                statusLabel.style.visibility = 'hidden'
            }
        })
        .catch(error => {
            alert("An error occurred in connecting to Access Servers. Please try again. Check logs for more information.")
            console.log("Error occurred in connecting to Access Servers: " + error)
            statusLabel.style.visibility = 'hidden'
        })
}