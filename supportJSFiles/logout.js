const params = location.search
var indivArgs = location.search.split('&')
if (indivArgs.length != 2) {
    location.href = origin + "/security/error?error=Invalid logout arguments were provided. Identity logout failed."
}
const authToken = indivArgs[0].split('=')[1]
const username = indivArgs[1].split('=')[1]

setTimeout(() => {
    axios({
        method: 'post',
        url: `${origin}/api/logoutIdentity`,
        headers: {
            'Content-Type': 'application/json',
            'AccessAPIKey': 'access@PRAKH0706!API.key#$69'
        },
        data: {
            "username": username,
            "authToken": authToken
        }
    })
        .then(response => {
            if (response.status == 200) {
                if (!response.data.startsWith("ERROR:")) {
                    if (!response.data.startsWith("UERROR:")) {
                        if (response.data.startsWith("SUCCESS:")) {
                            if (response.data == `SUCCESS: Logged out user ${username}.`) {
                                const heading = document.getElementById("heading")
                                heading.innerHTML = `Logged out ${username}!`

                                const statusLabel = document.getElementById("statusLabel")
                                statusLabel.innerHTML = `Re-directing to home page now...`

                                setTimeout(() => {
                                    location.href = location.origin
                                }, 1000)
                            } else {
                                alert("An unexpected logout success message was received from Access Servers. Please try again. Check console for more information.")
                                console.log("Unexpected success message: " + response.data)
                            }
                        } else {
                            alert("An unknown response was received from Access Servers. Please try again. Check console for more information.")
                            console.log("Unknown response recieved: " + response.data)
                        }
                    } else {
                        const statusLabel = document.getElementById("statusLabel")
                        statusLabel.innerHTML = `ERROR: ${response.data.substring('UERROR: '.length)}`
                        console.log(response.data)
                    }
                } else {
                    alert("An error occurred in logging out. Please try again. Check console for more information.")
                    console.log(response.data)
                }
            } else {
                alert("Failed to connect to Access Servers for logout. Please try again later. Check console for more information.")
                console.log("Non-200 response status code received from Access Servers.")
            }
        })
        .catch(error => {
            alert("An error occurred in connecting to Access Servers. Please try again later. Check console for more information.")
            console.log("Failed to connect to Access Servers, error: " + error)
        })
}, 2000)