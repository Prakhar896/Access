function deleteConfirmed() {

}

function backToPortal() {
    const url = document.URL
    var splitArray = url.split('/')
    splitArray.pop(9)
    
    var newURL = splitArray.join('/')
    window.location.href = newURL
}