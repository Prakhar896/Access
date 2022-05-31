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

        })
}