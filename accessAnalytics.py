import os, sys, json, random, subprocess, shutil
from dotenv import load_dotenv
load_dotenv()

class AccessAnalytics:
    analyticsData = {}
    # Metrics to calculate
            ## 1) Emails - Object
            ## 2) Requests - List
            ## 3) FileUploads - Integer
            ## 4) FileDeletions - Integer
            ## 5) FileDownloads - Integer
            ## 6) SignIns - Integer
            ## 7) SignOuts - Integer

    @staticmethod
    def permissionCheck():
        if 'AccessAnalyticsEnabled' not in os.environ:
            return False
        elif os.environ['AccessAnalyticsEnabled'] != 'True':
            return False
        else:
            return True

    @staticmethod
    def generateRandomID():
        possible = ['a', 'B', 'c', 'D', 'e', 'F', 'g', 'H', 'i', 'J', 'k', 'L', 'm', 'N', 'o', 'P', 'q', 'R', 's', 'T', 'u', 'V', 'w', 'X', 'y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        randomID = ""
        for i in range(0, 10):
            randomID += random.choice(possible)

        return randomID

    @staticmethod
    def prepEnvironmentForAnalytics():
        if not AccessAnalytics.permissionCheck():
            return "AAError: Access Analytics is not enabled and given permission to operate. Set AccessAnalyticsEnabled to True in the .env file to enable Analytics."

        if not os.path.isfile(os.path.join(os.getcwd(), 'analyticsData.txt')):
            with open('analyticsData.txt', 'w') as f:
                blankObject = {
                    "emails": {},
                    "requests": [],
                    "fileUploads": 0,
                    "fileDeletions": 0,
                    "fileDownloads": 0,
                    "signIns": 0,
                    "signOuts": 0
                }
                json.dump(blankObject, f)
                AccessAnalytics.analyticsData = blankObject
            return "AA: Environment prep successful."
        else:
            ## Check if file data is damaged
            try:
                fileData = json.load(open('analyticsData.txt', 'r'))
            except Exception as e:
                return "AAError: Failed to load data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
            for metric in ['emails', 'requests', 'fileUploads', 'fileDeletions', 'fileDownloads', 'signIns', 'signOuts']:
                if not metric in fileData:
                    return "AAError: analyticsData.txt file is damaged ('{}' metric is not present). Please delete the file and run environment prep again.".format(metric)
            AccessAnalytics.analyticsData = fileData
            return "AA: Environment prep successful."

    @staticmethod
    def loadDataFromFile(fileObject):
        if not AccessAnalytics.permissionCheck():
            return "AAError: Access Analytics is not enabled and given permission to operate. Set AccessAnalyticsEnabled to True in the .env file to enable Analytics."

        try:
            AccessAnalytics.analyticsData = json.load(fileObject)
        except Exception as e:
            return "AAError: Failed to load data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
        return True

    @staticmethod
    def saveDataToFile(fileObject):
        if not AccessAnalytics.permissionCheck():
            return "AAError: Access Analytics is not enabled and given permission to operate. Set AccessAnalyticsEnabled to True in the .env file to enable Analytics."
        
        try:
            json.dump(AccessAnalytics.analyticsData, fileObject)
        except Exception as e:
            return "AAError: Failed to save data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
        return True

    @staticmethod
    def newEmail(destEmail, text, subject):
        if subject not in ['Access Identity Login Alert', 'Access Folder Registered!', 'Access Portal OTP']:
            return "AAError: Subject is not valid."
        
        type = ''
        if subject == "Access Identity Login Alert":
            type = 'loginAlert'
        elif subject == 'Access Folder Registered!':
            type = 'folderRegistered'
        elif subject == 'Access Portal OTP':
            type = 'otp'
        
        emailID = AccessAnalytics.generateRandomID()

        try:
            AccessAnalytics.analyticsData['emails'][emailID] = {
                'destEmail': destEmail,
                'text': text,
                'subject': subject,
                'type': type
            }
            AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        except Exception as e:
            return "AAError: Failed to save email data to analytics data file. Error: {}".format(e)
        
        return True


print(AccessAnalytics.prepEnvironmentForAnalytics())
print(AccessAnalytics.newEmail('prakhar0706@gmail.com', 'Something', 'Access Portal OTP'))