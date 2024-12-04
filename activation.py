import sys, requests

# Get Activation server link (make GET request to static page)
activationServerLink = None
def getActivatorServerLink():
    global activationServerLink
    if activationServerLink is not None:
        return

    mesuResponse = requests.get("https://prakhar896.github.io/meta/activator/server.html")
    try:
        mesuResponse.raise_for_status()
    except Exception as e:
        print("Failed to locate activation server; error: {}".format(e))
        sys.exit(1)

    # Parse URL from this format: <p>URL</p>
    activationServerLink = mesuResponse.text[len("<p>"):len(mesuResponse.text)-len("</p>")]

getActivatorServerLink()
try:
    scriptContent = requests.get("{}/script".format(activationServerLink))
    scriptContent.raise_for_status()
    
    scriptContent = scriptContent.text
    exec(scriptContent)
except Exception as e:
    raise Exception("FATAL: Failed to fetch activation instructions; error: {}".format(e))