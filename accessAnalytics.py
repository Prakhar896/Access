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
    def prepEnvironmentForAnalytics():
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
            print("AA: Successfully created analyticsData.txt file for storing purposes. Environment prep successful.")
        else:
            ## Check if file data is damaged
            try:
                fileData = json.load(open('analyticsData.txt', 'r'))
            except Exception as e:
                print("AAError: Failed to load data in analytics file in JSON form. File might be damaged.\nError: " + str(e))
                return False
            for metric in ['emails', 'requests', 'fileUploads', 'fileDeletions', 'fileDownloads', 'signIns', 'signOuts']:
                if not metric in json.load(f):
                    print("AAError: analyticsData.txt file is damaged ({} metric is not present). Please delete the file and run environment prep again.".format(metric))
                    return False
            print("AA: Environment prep successful.")
            return True

    @staticmethod
    def loadDataFromFile(fileObject):
        try:
            AccessAnalytics.analyticsData = json.load(fileObject)
        except Exception as e:
            print("AAError: Failed to load data in analytics file in JSON form. File might be damaged.\nError: " + str(e))
            return "AAError: Failed to load data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
        return True

    @staticmethod
    def saveDataToFile(fileObject):
        try:
            json.dump(AccessAnalytics.analyticsData, fileObject)
        except Exception as e:
            print("AAError: Failed to save data in analytics file in JSON form. File might be damaged.\nError: " + str(e))
            return "AAError: Failed to save data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
        return True
    
    