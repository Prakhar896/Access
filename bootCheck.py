import os
# File to handle boot safety
def runBootCheck():
    ## Check for presence of requirements.txt file
    if not os.path.isfile(os.path.join(os.getcwd(), "requirements.txt")):
        print("WARNING: requirements.txt file was not found. This may cause booting issues if required dependencies do not exist.")

    ## Check for replit environment
    if os.path.isfile(os.path.join(os.getcwd(), "isInReplit.txt")):
        print("BOOTCHECK: Replit environment detected, re-installing libraries...")
        os.system("pip install -r requirements.txt")

    ## Check for python-dotenv presence
    try:
        import dotenv
    except:
        print("ERROR: Failed to import python-dotenv. Attempting to install...")
        os.system("pip install python-dotenv")
    
        try:
            import dotenv
        except:
            print("ERROR: Failed to re-import python-dotenv. Please install manually.")
            return False
    
    return True