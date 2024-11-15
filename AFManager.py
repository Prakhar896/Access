import os, shutil
from services import Logger

class AFManager:
    rootDir = "Directories"
    
    @staticmethod
    def rootDirPath():
        return os.path.join(os.getcwd(), AFManager.rootDir)
    
    @staticmethod
    def userDirPath(userID):
        return os.path.join(os.getcwd(), AFManager.rootDir, userID)
    
    @staticmethod
    def userFilePath(userID, filename):
        return os.path.join(os.getcwd(), AFManager.rootDir, userID, filename)
    
    @staticmethod
    def setup():
        if not os.path.isdir(AFManager.rootDirPath()):
            try:
                os.mkdir(AFManager.rootDirPath())
                Logger.log("AFM: Root directory created.")
            except Exception as e:
                Logger.log("AFM: Error occurred in creating root directory: {}".format(e))
                return False
        return True

    @staticmethod
    def registerFolder(userID):
        if os.path.isdir(AFManager.userDirPath(userID)):
            return AFMError("Folder already exists.")
        
        try:
            os.mkdir(AFManager.userDirPath(userID))
            Logger.log("AFM: Directory registered for user '{}'.".format(userID))
        except Exception as e:
            return AFMError("Error occurred in creating folder: {}".format(e))
        
        return True

    @staticmethod
    def checkIfFolderIsRegistered(userID):
        if os.path.isdir(AFManager.userDirPath(userID)):
            return True
        else:
            return False

    @staticmethod
    def deleteFolder(userID):
        if AFManager.checkIfFolderIsRegistered(userID):
            try:
                shutil.rmtree(AFManager.userDirPath(userID), ignore_errors=True)
                return True
            except Exception as e:
                return AFMError("Error occurred in deleting folder: {}".format(e))
        else:
            return AFMError("Folder does not exist.")

    @staticmethod
    def getFilenames(userID):
        if AFManager.checkIfFolderIsRegistered(userID):
            filenames = [f for f in os.listdir(AFManager.userDirPath(userID)) if os.path.isfile(AFManager.userFilePath(userID, f))]
            return filenames
        else:
            return AFMError("Folder does not exist.")

    @staticmethod
    def deleteFile(userID, filename):
        if AFManager.checkIfFolderIsRegistered(userID):
            if os.path.isfile(AFManager.userFilePath(userID, filename)):
                try:
                    os.remove(AFManager.userFilePath(userID, filename))
                    return True
                except Exception as e:
                    return AFMError("Error occurred in deleting file: {}".format(e))
            else:
                return AFMError("File does not exist.")
        else:
            return AFMError("Folder does not exist.")


class AFMError:
    def __init__(self, message: str) -> None:
        self.message = "AFMError: " + message
        
    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return self.message