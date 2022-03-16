const statusLabel = document.getElementById("statusLabel")
var username = statusLabel.innerText.substring("Registering folder for ".length, statusLabel.innerText.length - "...".length)
console.log(username)