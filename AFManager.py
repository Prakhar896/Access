import os

class AFManager:

    @staticmethod
    def registerFolder(username):
        if os.path.isdir(os.path.join(os.getcwd(), 'AccessFolders', username)):
            return AFMError.folderAlreadyRegistered
        
        os.mkdir(os.path.join(os.getcwd(), 'AccessFolders', username))
        print("AFM: User {} registered an Access Folder.")
        return "Access Folder for {} registered.".format(username)

    @staticmethod
    def checkIfFolderIsRegistered(username):
        if os.path.isdir(os.path.join(os.getcwd(), 'AccessFolders', username)):
            return True
        else:
            return False
    

class AFMError(Exception):
    def __init__(self, message):
        self.message = message

    folderAlreadyRegistered = "AFMError: The Access Folder is already registered for the username."

    @staticmethod
    def checkIfErrorMessage(msg):
        msgsArray = [
            AFMError.folderAlreadyRegistered
        ]
        
        if msg in msgsArray:
            return True
        else:
            return False

