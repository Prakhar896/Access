import os
from importlib.metadata import distributions

class BootCheck:
    @staticmethod
    def getInstallations() -> list:
        pkgs = []
        for x in distributions():
            pkgs.append(x.name)
        return pkgs
    
    @staticmethod
    def checkDependencies():
        requiredDependencies = [
            "Flask",
            "Flask-Cors",
            "requests",
            "python-dotenv",
            "passlib",
            "firebase-admin",
            "getmac"
        ]
        
        deps = BootCheck.getInstallations()
        for req in requiredDependencies:
            if req not in deps:
                raise Exception("BOOTCHECK ERROR: Required package '{}' not found.".format(req))
        
        return True
    
    @staticmethod
    def checkEnvVariables():
        from dotenv import load_dotenv
        load_dotenv()
        
        requiredEnvVariables = [
            "APP_SECRET_KEY",
            "AccessAnalyticsEnabled",
            "RuntimePort",
            "LOGGING_ENABLED",
            "SYSTEM_URL"
        ]
        
        for var in requiredEnvVariables:
            if var not in os.environ:
                raise Exception("BOOTCHECK ERROR: Required environment variable '{}' was not found.".format(var))
            if var == "EMAILING_ENABLED" and os.environ[var] == "True" and ("SENDER_EMAIL" not in os.environ or "SENDER_EMAIL_APP_PASSWORD" not in os.environ):
                raise Exception("BOOTCHECK ERROR: 'EMAILING_ENABLED' is True but 'SENDER_EMAIL' and 'SENDER_EMAIL_APP_PASSWORD' are not set.")
            
        optionalEnvVariables = [
            "DEBUG_MODE"
        ]
        notFound = []
        for var in optionalEnvVariables:
            if var not in os.environ:
                notFound.append(var)
        
        if len(notFound) > 0:
            print("BOOTCHECK WARNING: Optional environment variables {} not found.".format(', '.join(notFound)))
            
        return True
    
    @staticmethod
    def check():
        return BootCheck.checkDependencies() and BootCheck.checkEnvVariables()