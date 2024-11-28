import os, sys, json, shutil, datetime, copy

class Config:
    file = "config.json"
    defaultConfig = {
        "fileExtensions": ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'heic', 'mov', 'mp4', 'docx', 'pptx', 'py', 'swift', 'js', 'zip'],
        "allowedDirectorySize": 16,
        "allowedRequestSize": 16,
        "maxFileCount": 20,
        "systemLock": False
    }

    def __init__(self):
        self.config = {}
        reloadSuccessful = self.reload()
        if not reloadSuccessful:
            print("CONFIG INIT: Failed to initialise config instance; falling back on default config.")
            self.config = Config.defaultConfig
            self.dump()
        
    def getFileExtensions(self):
        return self.config['fileExtensions'] if 'fileExtensions' in self.config and isinstance(self.config['fileExtensions'], list)  else []
    
    def getAllowedDirectorySize(self):
        return (self.config['allowedDirectorySize'] if 'allowedDirectorySize' in self.config and isinstance(self.config['allowedDirectorySize'], int) else 0) * 1024 * 1024
    
    def getAllowedRequestSize(self):
        return self.config['allowedRequestSize'] if 'allowedRequestSize' in self.config and isinstance(self.config['allowedRequestSize'], int) else 0
    
    def getMaxFileCount(self):
        return self.config['maxFileCount'] if 'maxFileCount' in self.config and isinstance(self.config['maxFileCount'], int) else 0
    
    def getSystemLock(self):
        return self.config['systemLock'] if 'systemLock' in self.config and isinstance(self.config['systemLock'], bool) else False

    def dump(self):
        with open(Config.file, "w") as f:
            json.dump(self.config, f)

        return True

    def reload(self):
        if not os.path.isfile(os.path.join(os.getcwd(), Config.file)):
            with open(Config.file, "w") as f:
                json.dump(Config.defaultConfig, f)

            self.config = Config.defaultConfig
        else:
            try:
                with open(Config.file, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                print("CONFIG LOAD ERROR: {}".format(e))
                return False
        
        for reqParam in ['fileExtensions', 'allowedDirectorySize', 'allowedRequestSize', 'maxFileCount', 'systemLock']:
            if reqParam not in self.config:
                if reqParam == "fileExtensions":
                    self.config["fileExtensions"] = []
                elif reqParam == "allowedDirectorySize":
                    self.config["allowedDirectorySize"] = 16
                elif reqParam == "allowedRequestSize":
                    self.config["allowedRequestSize"] = 16
                elif reqParam == "maxFileCount":
                    self.config["maxFileCount"] = 20
                elif reqParam == "systemLock":
                    self.config["systemLock"] = False
        
        return True

## General Settings function
def manageFileExtensions(configManager: Config):
    def currentFileExtensions():
        print("Current allowed file extensions: ")
        print("\t" + ", ".join(configManager.config['fileExtensions']))
    currentFileExtensions()
    print()
    print("To add, type 'a <extension here, e.g pdf>'.")
    print("To remove, type 'r <extension here, e.g pdf>'.")
    print("To remove all, type 'r -all'.")
    print("To return to main menu, type '0'.")
    print()

    exitToMainMenu = False
    while not exitToMainMenu:
        command = input("Enter command: ")
        if command[0] not in ["0", "a", "r"]:
            print("Invalid command provided. Please try again.")
            continue
        elif command[0] == "0":
            exitToMainMenu = True
            continue
            
        extensionsUpdated = False
        if command == "r -all":
            configManager.config['fileExtensions'] = []
            configManager.dump()
            print("Successfully removed all file extensions.")
            continue
        elif command[0] == "r":
            targetExtensions = command.split(" ")[1::]
            for targetExtension in targetExtensions:
                if targetExtension not in configManager.config['fileExtensions']:
                    print("Extension '{}' is not in the list of allowed file extensions.".format(targetExtension))
                    continue
                else:
                    configManager.config['fileExtensions'].remove(targetExtension)
                    configManager.dump()
                    print("Successfully removed extension '{}'.".format(targetExtension))
                    extensionsUpdated = True
                    continue
        elif command[0] == "a":
            targetExtensions = command.split(" ")[1::]
            for targetExtension in targetExtensions:
                if targetExtension in configManager.config["fileExtensions"]:
                    print("Extension '{}' is already in the list of allowed file extensions.".format(targetExtension))
                    continue
                else:
                    configManager.config['fileExtensions'].append(targetExtension)
                    configManager.dump()
                    print("Successfully added extension '{}'.".format(targetExtension))
                    extensionsUpdated = True
                    continue
            
        print()
        if extensionsUpdated:
            currentFileExtensions()
            extensionsUpdated = False

    return

def manageDirectorySize(configManager: Config):
    print("Current allowed directory size: {} MB".format(configManager.config["allowedDirectorySize"]))
    newDirectorySize = input("Enter new directory size (in MB) or '0' to return: ")

    while not newDirectorySize.isdigit():
        print("Invalid directory size provided. Please try again.")
        newDirectorySize = input("Enter new directory size (in MB) or '0' to return: ")

    newDirectorySize = int(newDirectorySize)
    if newDirectorySize == 0:
        return
    else:
        configManager.config["allowedDirectorySize"] = newDirectorySize
        configManager.dump()
        print()
        print("Successfully updated directory size to {} MB.".format(newDirectorySize))
        
def manageRequestSize(configManager: Config):
    print("Current allowed request size: {} MB".format(configManager.config["allowedRequestSize"]))
    newRequestSize = input("Enter new request size (in MB) or '0' to return: ")

    while not newRequestSize.isdigit():
        print("Invalid request size provided. Please try again.")
        newRequestSize = input("Enter new request size (in MB) or '0' to return: ")

    newRequestSize = int(newRequestSize)
    if newRequestSize == 0:
        return
    else:
        configManager.config["allowedRequestSize"] = newRequestSize
        configManager.dump()
        print()
        print("Successfully updated request size to {} MB.".format(newRequestSize))
        
def manageFileCount(configManager: Config):
    print("Current maximum file count: {}".format(configManager.config["maxFileCount"]))
    newFileCount = input("Enter new file count or '0' to return: ")

    while not newFileCount.isdigit():
        print("Invalid file count provided. Please try again.")
        newFileCount = input("Enter new file count or '0' to return: ")

    newFileCount = int(newFileCount)
    if newFileCount == 0:
        return
    else:
        configManager.config["maxFileCount"] = newFileCount
        configManager.dump()
        print()
        print("Successfully updated file count to {}.".format(newFileCount))