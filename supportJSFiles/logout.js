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
        
    })
}, 2000)