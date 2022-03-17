import os

class AFManager:

    @staticmethod
    def registerFolder(username):
        if os.path.isdir(os.path.join(os.getcwd(), 'AccessFolders', username)):
            return AFMError.folderAlreadyRegistered
        
        try:
            os.mkdir(os.path.join(os.getcwd(), 'AccessFolders', username))
            print("AFM: User {} registered an Access Folder.".format(username))
        except Exception as e:
            print("AFMError: {}".format(e))
            return AFMError.unknownError
        return "Access Folder for {} registered.".format(username)

    @staticmethod
    def checkIfFolderIsRegistered(username):
        if os.path.isdir(os.path.join(os.getcwd(), 'AccessFolders', username)):
            return True
        else:
            return False

    @staticmethod
    def deleteFolder(username):

        if os.path.isdir(os.path.join(os.getcwd(), 'AccessFolders', username)):
            try:
                os.rmdir(os.path.join(os.getcwd(), 'AccessFolders', username))
            except Exception as e:
                print("AFMError: {}".format(e))
                return AFMError.unknownError
        else:
            return AFMError.folderDoesNotExist

    @staticmethod
    def getFilenames(username):
        if os.path.isdir(os.path.join(os.getcwd(), 'AccessFolders', username)):
            filenames = [f for f in os.listdir(os.path.join(os.getcwd(), 'AccessFolders', username)) if os.path.isfile(os.path.join(os.path.join(os.getcwd(), 'AccessFolders', username), f))]
            if filenames == []:
                filenames = None
            return filenames
        else:
            return AFMError.folderDoesNotExist

class AFMError(Exception):
    def __init__(self, message):
        self.message = message

    folderAlreadyRegistered = "AFMError: The Access Folder is already registered for the username."
    unknownError = "AFMError: There was an unknown error in performing the AFM action. Check console for more information."
    folderDoesNotExist = "AFMError: No such Access Folder exists."

    @staticmethod
    def checkIfErrorMessage(msg):
        msgsArray = [
            AFMError.folderAlreadyRegistered,
            AFMError.unknownError,
            AFMError.folderDoesNotExist
        ]
        
        if msg in msgsArray:
            return True
        else:
            return False

