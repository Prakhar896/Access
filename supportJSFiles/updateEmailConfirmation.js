function sendOTPVerification() {

}

function updateEmail() {

}

document.getElementById("newEmail")
    .addEventListener("keyup", (event) => {
        event.preventDefault()
        if (event.keyCode === 13) {
            document.getElementById("sendOTPButton").click();
        }
    })

document.getElementById("otpField")
    .addEventListener("keyup", (event) => {
        event.preventDefault()
        if (event.keyCode === 13) {
            document.getElementById("updateEmailButton").click();
        }
    })