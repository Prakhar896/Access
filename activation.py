import os, sys, shutil, subprocess, requests, datetime, random, time, platform, getpass

# Get Activation server link (make GET request to static page)
activationServerLink = None
def getActivatorServerLink():
    global activationServerLink

    mesuResponse = requests.get("https://prakhar896.github.io/meta/activator/server.html")
    try:
        mesuResponse.raise_for_status()
    except Exception as e:
        print("Failed to locate activation server; error: {}".format(e))

    # Parse URL from this format: <p>URL</p>
    activationServerLink = mesuResponse.text[len("<p>"):len(mesuResponse.text)-len("</p>")]

licenseKeyFileContentTemplate = """License Key: {}
CSN: {}
HSN: {}
Last License Check: {}

You may view your product copy activation details and your HSN account at {}/account/login?hsn={}

DO *NOT* MODIFY THIS FILE. THIS FILE CONTAINS A LICENSE KEY ASSOCIATED WITH THIS COPY OF THE SOURCE CODE. THE KEY WAS AUTOMATICALLY GENERATED WHEN THIS COPY WAS ACTIVATED.
THE KEY IS USED PERIODICALLY TO CHECK FOR VALIDITY WITH SERVERS ONLINE. ACTIVATION COMES AT NO COST AND NO PRIVATE INFORMATION IS SENT ONLINE.
"""

def getMachine_addr():
	os_type = sys.platform.lower()
	if "darwin" in os_type:
		command = "ioreg -l | grep IOPlatformSerialNumber"
	elif "linux" in os_type:
		command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"
	elif "win" in os_type:
		command = "wmic bios get serialnumber"
	return os.popen(command).read().replace("\n","").replace("	","").replace(" ","")

def checkForActivation():
    if not os.path.exists(os.path.join(os.getcwd(), "licensekey.txt")):
        return False
    else:
        with open("licensekey.txt", 'r') as f:
            # If last license check is more than 14 days prior, return False
            if (datetime.datetime.now() - datetime.datetime.strptime(f.readlines()[3].split("\n")[0][len("Last License Check: ")::], "%Y-%m-%d %H:%M:%S")).days > 14:
                return "Verify"
            else:
                return True

def makeKVR(productID, copyVersion):
    getActivatorServerLink()
    print("---------")
    print("License key needs to be re-verified (every 14 days); initializing key verification request...")
    time.sleep(2)

    if not os.path.isfile(os.path.join(os.getcwd(), 'licensekey.txt')):
        print("ACTIVATION: Failed to verify license key of copy as licensekey.txt file cannot be found in root of directory. Please ensure copy is activated.")
        print("---------")
        sys.exit(1)
    
    hsn = None
    csn = None
    licenseKey = None
    try:
        with open('licensekey.txt', 'r') as f:
            lines = f.readlines()
            licenseKey = lines[0][len("License Key: "):-1]
            csn = lines[1][len("CSN: "):-1]
            hsn = lines[2][len("HSN: "):-1]
    except Exception as e:
        print()
        print("ACTIVATIONERROR: Could not parse copy information (csn, hsn and license key) from licensekey.txt file. This could be becuase it was modified. Please delete the licensekey.txt file and re-activate this copy. Error: {}".format(e))
        sys.exit(1)
    
    # Connect to Activator servers
    print()
    print("Connecting to Activator servers...")
    time.sleep(0.5)

    response = requests.post(
        url=activationServerLink + '/api/verifyKey',
        json={
            "hsn": hsn,
            "csn": csn,
            "productID": productID,
            "licenseKey": licenseKey,
            "copyVersion": copyVersion
        }
    )

    print()
    print("Verifying key...")
    time.sleep(1)
    print()

    try:
        response.raise_for_status()
        if response.text == "True":
            print("License key successfully verified! Continuing with program execution...")
            time.sleep(0.5)

            with open('licensekey.txt', 'w') as f:
                f.write(licenseKeyFileContentTemplate.format(
                    licenseKey,
                    csn,
                    hsn,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    activationServerLink,
                    hsn
                ))
            return
        elif response.text == "False":
            print("License key is incorrect. This copy cannot be run. Please delete the licensekey.txt file and re-activate this copy.")
            sys.exit(1)
        elif response.text.startswith("DEACTIVATED:"):
            print("NOTICE: THIS COPY HAS BEEN DE-ACTIVATED. See response from Activator servers below.")
            print()
            print("Response: {}".format(response.text[len("DEACTIVATED: ")::]))
            print()
            
            # Remove license key file
            os.remove(os.path.join(os.getcwd(), 'licensekey.txt'))

            print("If you wish to re-activate this copy, please run this copy's code once again.")
            print("--------")
            sys.exit(0)
        else:
            print("Unknown response received from Activator servers; response: {}".format(response.text))
            print("License key verification request has failed. If this issue persists, delete the licensekey.txt file and re-run this copy's code.")
            sys.exit(1)
    except Exception as e:
        print("There was an error in making the license key verification request; error: {}".format(e))
        print("License key verification request has failed. If this issue persists, delete the licensekey.txt file and re-run this copy's code.")
        sys.exit(1)

def initActivation(productID, copyVersion):
    getActivatorServerLink()
    # Scan libraries to ensure getmac is installed
    try:
        import getmac
    except ImportError:
        print("ACTIVATION: getmac not installed; attempting to install...")
        print("ACTIVATION: If attempt fails, please manually install all needed libraries by running 'pip install -r requirements.txt'")
        time.sleep(0.5)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "getmac"])
        import getmac
        print()
        print("Successfully installed!")


    # Let user know
    print("---")
    # TODO: Add link in intro message
    print("""
    Hi there! Thank you for downloading and using this product!

    Before you get started on using the product, activation is recommended. Do not worry! Activation comes at no cost
    and no private information of yours is sent online. 
    
    Activation simply allows for a better user experience for you, as you will be able to manage this copy of this product
    and others you may download later on the Activator service. If this is your first copy, you will be able to login to the
    Activator service after activation by clicking the link in the licensekey.txt file that will be generated. (Activation 
    automatically creates an account for you!)

    Activation will start soon and will take very little time. Should you choose to remain anonymous, you can type 'anon'
    in the username prompt that will come up next.

    For more information, visit: {}
    """.format(activationServerLink))
    time.sleep(4)
    print()

    username = input("Enter your username (will be linked to your Activator account): ")
    if username.lower() == 'anon':
        username = "Anonymous"

    print()
    print("Activator: Generating unique identifiers for this copy...please wait!")
    time.sleep(1)

    # Get MAC address of computer
    macAddress = getmac.get_mac_address()

    machine_serial = getMachine_addr()
    wantedString = machine_serial[-10::]
    for char in wantedString:
        if not char.isalnum():
            wantedString = wantedString.replace(char, "")

    # Craft HSN
    macPortion = ''.join(macAddress.split(':')[1:5])
    hsn = macPortion + wantedString

    # Craft CSN
    csnMacPortion = ''.join([macAddress.split(':')[0], macAddress.split(':')[5]])
    currentDatetime = datetime.datetime.now().strftime("%Y%S%d%H%M%m")

    draftCSN = csnMacPortion + currentDatetime + productID
    currentSum = 0
    for char in draftCSN:
        if char.isdigit():
            currentSum += int(char)

    addOnString = ''
    diff = 256 - currentSum
    while diff > 0:
        numChoices = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        choice = random.choice(numChoices)
        while choice > diff:
            choice = random.choice(numChoices)
        addOnString += str(choice)
        diff -= choice

    csn = draftCSN + addOnString
    # print(hsn, csn)

    # Determine operating system
    os_type = platform.platform()

    print()
    print("Connecting to Activator servers...")
    time.sleep(1)

    print()
    print("Activating product...")
    print()

    licenseKey = None
    requestBody = {
                "csn": csn,
                "hsn": hsn,
                "username": username,
                "productID": productID,
                "macAddress": macAddress,
                "copyVersion": copyVersion,
                "operatingSystem": os_type
            }
    # Request while loop
    while True:
        response = requests.post(
            url=activationServerLink + '/api/activateCopy',
            json=requestBody,
            headers={
                "Content-Type": 'application/json'
            }
        )

        try:
            response.raise_for_status()
            if response.text.startswith("ERROR:"):
                raise Exception(response.text)
            elif response.text.startswith("UERROR:"):
                if 'password' in requestBody:
                    # Incorrect password
                    print("SERVER RESPONSE:", response.text[len("UERROR: ")::])
                    password = getpass.getpass("Please enter your Activator account password to authorise activation: ")
                    requestBody['password'] = password
                    print("Attempting to complete activation...")
                    print()
                    continue
                else:
                    raise Exception("User error occurred in activation; error: " + response.text[len("UERROR: ")::])
            elif response.text.startswith("CONTINUE:"):
                print("SERVER RESPONSE:", response.text[len("CONTINUE: ")::])
                password = getpass.getpass("Please enter your Activator account password to authorise activation: ")
                requestBody['password'] = password
                print("Attempting to complete activation...")
                print()
                continue
            elif not response.text.startswith("SUCCESS"):
                raise Exception("Unknown response received from service: {}".format(response.text))

            # Success case
            licenseKey = response.text.split(" ")[1]
            break
        except Exception as e:
            print("Product activation unsuccessful; error: {}".format(e))
            sys.exit(1)

    print("Product activation successful! Your license key is: {}".format(licenseKey))
    print("Writing activation data to licensekey.txt...please wait!")
    time.sleep(1)

    # Write license key to file
    with open("licensekey.txt", "w") as f:
        fileContent = licenseKeyFileContentTemplate.format(
            licenseKey,
            csn,
            hsn,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            activationServerLink,
            hsn
        )

        f.write(fileContent)

    print("Done! You may now use this copy of the product. Continuing with program execution...")
    print("---")

    return
