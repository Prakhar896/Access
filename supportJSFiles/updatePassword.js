function updatePassword() {

}

document.getElementById("confirmPasswordField")
    .addEventListener("keyup", (event) => {
        event.preventDefault()
        if (event.keyCode === 13) {
            document.getElementById("updatePasswordButton").click();
        }
    })