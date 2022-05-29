function redirectEmailConfirmation() {
    var arrayURL = url.split("/");
    arrayURL = arrayURL.slice(0, 7).join('/') + "/settings/idInfo/updateEmail"
    window.location.href = arrayURL;
}

function sendOTPVerification() {

}

function updateEmail() {
    
}