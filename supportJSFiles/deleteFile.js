function deleteConfirmed() {
    const sourceField = document.getElementById("usernameSourceField")
    const username = sourceField.innerHTML.substring(0, sourceField.innerHTML.indexOf(','))
    const filename = sourceField.innerHTML.substring(sourceField.innerHTML.indexOf('"') + 1, sourceField.innerHTML.length - 2)

    const statusLabel = document.getElementById("statusLabel")
    statusLabel.style.visibility = "visible"

    axios({
        method: 'post',
        url: `${origin}/api/deleteFile`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            "username": username,
            "filename": filename
        }
    })
    .then(response => {
        if (response.status == 200) {
            if (!response.data.startsWith("ERROR:")) {
                if (!response.data.startsWith("UERROR:")) {
                    if (response.data.startsWith("SUCCESS:")) {
                        if (response.data == `SUCCESS: File ${filename} belonging to user ${username} was successfully deleted.`) {
                            statusLabel.innerHTML = "File successfully deleted! Re-directing back to portal..."
                            setTimeout(() => {
                                backToPortal()
                            }, 2000)
                        } else {
                            statusLabel.style.visibility = "hidden"
                            statusLabel.innerHTML = "Processing..."
                            alert("An unknown success message was received from Access Servers. Please try again. Check console for more information.")
                            console.log(`Unexpected SUCCESS Message Received: ${response.data}`)
                        }
                    } else {
                        statusLabel.style.visibility = "hidden"
                        statusLabel.innerHTML = "Processing..."
                        alert("An unknown response was received from Access Servers. Please try again. Check console for more information.")
                        console.log(`Received unknown non-error and non-success message: ${response.data}`)
                    }
                } else {
                    statusLabel.style.visibility = "visible"
                    statusLabel.innerHTML = `Error: ${response.data.substring('UERROR: '.length)}`
                    console.log(response.data)
                }
            } else {
                statusLabel.style.visibility = "hidden"
                statusLabel.innerHTML = "Processing..."
                alert("An error occurred in deleteing the file. Please try again. Check console for more information.")
                console.log(response.data)
            }
        } else {
            statusLabel.style.visibility = "hidden"
            statusLabel.innerHTML = "Processing..."
            alert("Failed to connect to Access Servers. Please try again later. Check console for more information.")
            console.log("Non-200 status code response was received from servers: " + response.data)
        }
    })
    .catch(error => {
        statusLabel.style.visibility = "hidden"
        statusLabel.innerHTML = "Processing..."
        alert("An error occurred in connecting to Access Servers. Please try again later. Check console for more information.")
        console.log("Error in connecting to Access Servers: " + error)
    })
}

function backToPortal() {
    const url = document.URL
    var splitArray = url.split('/')
    splitArray.pop(9)
    
    var newURL = splitArray.join('/')
    window.location.href = newURL
}