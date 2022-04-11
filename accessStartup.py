from accessAnalytics import *

print("Welcome to Access Startup!")
print()
print("Here you can manage and run all things Access!")
print()
print()
print("""
Startup Choices - What would you like to do?

    1) Access Boot
    2) Access Meta Settings
    3) Access CheckUp
    4) Access Analytics - Crunch Data


""")

while True:
    try:
        choice = int(input("Enter your choice number: "))
        break
    except:
        print("Invalid choice provided.")
        continue

if choice == 1:
    ## Begin Access Boot
    from main import *
    if __name__ == "__main__":
        # Boot Authorisation
        if os.path.isfile(os.path.join(os.getcwd(), 'authorisation.txt')):
            try:
                with open('authorisation.txt', 'r') as f:
                    decoded = CertAuthority.decodeFromB64(f.read())
                    code = getpass("MAIN: Enter your Boot Authorisation Code to begin Access Boot: ")
                    if code != decoded:
                        print("MAIN: Boot Authorisation Code is incorrect. Main will not proceed with the boot.")
                        sys.exit(1)
                    else:
                        print()
            except Exception as e:
                print("MAIN: Failed to load and ask for boot authorisation code. Error: {}".format(e))
                print("MAIN: Main will not proceed with the boot.")
                sys.exit(1)

    # Load certificates
    CAresponse = CertAuthority.loadCertificatesFromFile(fileObject=open('certificates.txt', 'r'))
    if CAError.checkIfErrorMessage(CAresponse):
        print(CAresponse)
        sys.exit(1)
    else:
        print(CAresponse)
  
    # Expire old certificates and save new data
    CertAuthority.expireOldCertificates()
    CertAuthority.saveCertificatesToFile(open('certificates.txt', 'w'))

    ## Expire auth tokens
    tempIdentities = accessIdentities
    accessIdentities = expireAuthTokens(tempIdentities)
    json.dump(accessIdentities, open('accessIdentities.txt', 'w'))

    ## Set up Access Analytics
    if AccessAnalytics.permissionCheck():
        AAresponse = AccessAnalytics.prepEnvironmentForAnalytics()
        if AAresponse.startswith("AAError:"):
            print("MAIN: Error in getting Analytics to prep environment. Response: {}".format(AAresponse))
            print()
            print("MAIN: Would you like to enable Analytics Recovery Mode?")
            recoveryModeAction = input("Type 'yes' or 'no': ")
            if recoveryModeAction == "yes":
                AccessAnalytics.analyticsRecoveryMode()
            elif recoveryModeAction == "no":
                print("MAIN: Recovery mode was not enabled. Access Boot is aborted.")
                sys.exit(1)
            else:
                print("MAIN: Invalid action provided. Access Boot is aborted.")
                sys.exit(1)
        elif AAresponse != "AA: Environment prep successful.":
            print("MAIN: Unknown response when attempting to get Analytics to prep environment. Response: {}".format(AAresponse))
            print()
            print("MAIN: Would you like to enable Analytics Recovery Mode?")
            recoveryModeActionTwo = input("Type 'yes' or 'no': ")
            if recoveryModeActionTwo == "yes":
                AccessAnalytics.analyticsRecoveryMode()
            elif recoveryModeActionTwo == "no":
                print("MAIN: Recovery mode was not enabled. Access Boot is aborted.")
                sys.exit(1)
            else:
                print("MAIN: Invalid action provided. Access Boot is aborted.")
                sys.exit(1)
        else:
            print(AAresponse)
    else:
        print("MAIN: Notice!!! AccessAnalytics is not enabled and will not be setup and run.")

    ## Port check
    if 'RuntimePort' not in os.environ:
        print("MAIN: RuntimePort environment variable is not set in .env file. Access cannot be booted without a valid port set. Please re-boot Access after setting RuntimePort.")
        sys.exit(1)
    elif not os.environ['RuntimePort'].isdigit():
        print("MAIN: RuntimePort environment variable has an invalid value. Port value must be an integer.")
        sys.exit(1)
      
    print("All services are online; boot pre-processing and setup completed.")
    print()
    print("Booting Access...")
    print()
    app.run(host='0.0.0.0', port=int(os.environ['RuntimePort']))

    
    print()
    print("STARTUP: Access Startup will now close.")
elif choice == 2:
    # Meta Settings - Make authorisation code, Run Access Analytics Recovery Mode
    pass
elif choice == 3:
    # Run Access CheckUp
    print()
    print("Startup: Initialising Access CheckUp service...")
    print()
    print()
    import accessCheckup
    print()
    print("Startup: Exiting startup...")
elif choice == 4:
    ## Run Crunch Data in Access Analytics
    print("Running data analysis function...")
    print()
    print()
    AccessAnalytics.crunchData()
    print()
    print("STARTUP: Access Startup will now close.")
