const statusLabel = document.getElementById("statusLabel")
var username = statusLabel.innerHTML.substring("Registering folder for ".length, statusLabel.innerHTML.length - "...".length)

function registerClicked() {
    statusLabel.style.visibility = "visible"

    axios({
        method: 'post',
        url: `${origin}/api/registerFolder`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            'username': username
        }
    })
    .then(response => {
        if (!response.data.startsWith("ERROR:")) {
            if (response.data.startsWith("SUCCESS:")) {
                if (response.data == `SUCCESS: Access Folder for ${username} registered!`) {
                    console.log("Folder registered!")
                    setTimeout(() => {
                        location.reload()
                    }, 1000)
                } else {
                    alert("An unexpected registration success response was recieved from Access Servers. Please try again. Check logs for more information.")
                    console.log(`Unexpected Success Message: ${response.data}`)
                    statusLabel.style.visibility = "hidden"
                }
            } else {
                alert("An unknown response was received when trying to register your folder from Access Servers. Please try again. Check logs for more information.")
                console.log(`Unknown response recieved: ${response.data}`)
                statusLabel.style.visibility = "hidden"
            }
        } else if (response.data == "ERROR: Folder for the Access Identity is already registered.") {
            setTimeout(() => {
                location.reload()
            }, 1000)
        } else {
            alert("An error occurred in registering your Access Folder. Please try again. Check logs for more information.")
            console.log(response.data)
            statusLabel.style.visibility = "hidden"
        }
    })
}