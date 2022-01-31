function signin() {
    const emailField = document.getElementById("floatingEmail")
    const passwordField = document.getElementById("floatingPassword")

    if (!emailField.value || emailField.value == "" || !passwordField.value || passwordField.value == "") {
        alert("One or more fields is empty. Please try again.")
        return
    }

    
}