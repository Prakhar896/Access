const statusLabel = document.getElementById("statusLabel")

function sendOTP() {
    const usernameField = document.getElementById("usernameField")
    const emailField = document.getElementById("emailField")
    const passwordField = document.getElementById("passwordField")

    if (!usernameField.value || usernameField.value == "" || !emailField.value || emailField.value == "" || !passwordField.value || passwordField.value == "") {
        alert("One or more fields are empty. Please try again.")
        return
    }

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
}