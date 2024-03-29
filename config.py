import os, sys, json, shutil, datetime, copy

class Config:
    defaultConfig = {
        "fileExtensions": ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'heic', 'mov', 'mp4', 'docx', 'pptx', 'py', 'swift', 'js', 'zip'],
        "allowedFileSize": 16
    }

    def __init__(self):
        self.config = {}
        reloadSuccessful = self.reload()
        if not reloadSuccessful:
            print("CONFIG INIT: Failed to initialise config instance; falling back on default config.")
            self.config = Config.defaultConfig
        return

    def dump(self):
        with open("config.txt", "w") as f:
            json.dump(self.config, f)

        return True

    def reload(self):
        if not os.path.isfile(os.path.join(os.getcwd(), "config.txt")):
            with open("config.txt", "w") as f:
                json.dump(Config.defaultConfig, f)

            self.config = Config.defaultConfig
        else:
            try:
                with open("config.txt", "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                print("CONFIG LOAD ERROR: {}".format(e))
                return False
            
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

def manageFileSize(configManager: Config):
    print("Current allowed file size: {} MB".format(configManager.config["allowedFileSize"]))
    newFileSize = input("Enter new file size (in MB) or '0' to return: ")

    while not newFileSize.isdigit():
        print("Invalid file size provided. Please try again.")
        newFileSize = input("Enter new file size (in MB) or '0' to return: ")

    newFileSize = int(newFileSize)
    if newFileSize == 0:
        return
    else:
        configManager.config["allowedFileSize"] = newFileSize
        configManager.dump()
        print()
        print("Successfully updated file size to {} MB.".format(newFileSize))