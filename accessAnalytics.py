import os, sys, json, random, subprocess, shutil, uuid
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
            ## 8) POST Requests - Integer

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
        randomID = uuid.uuid4().hex

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
                    "signOuts": 0,
                    "postRequests": 0
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
            for metric in ['emails', 'requests', 'fileUploads', 'fileDeletions', 'fileDownloads', 'signIns', 'signOuts', "postRequests"]:
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
            # return "AAError: Access Analytics is not enabled and given permission to operate. Set AccessAnalyticsEnabled to True in the .env file to enable Analytics."
            return False
        
        try:
            json.dump(AccessAnalytics.analyticsData, fileObject)
        except Exception as e:
            return "AAError: Failed to save data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
        return True

    @staticmethod
    def newEmail(destEmail, text, subject, usernameAttachedToEmail="Not provided."):
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
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails paramter not found in memory location data)"
            AccessAnalytics.analyticsData['emails'][emailID] = {
                'destEmail': destEmail,
                'text': text,
                'subject': subject,
                'type': type,
                'username': usernameAttachedToEmail
            }
            response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
            if isinstance(response, str):
                if response.startswith("AAError:"):
                    return response
        except Exception as e:
            return "AAError: Failed to save email data to analytics data file. Error: {}".format(e)
        
        return True
    
    @staticmethod
    def newRequest(path):
        if not path.startswith('/'):
            return "AAError: Given path does not start with a forward-slash."
        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
            AccessAnalytics.analyticsData['requests'].append(path)
        except Exception as e:
            return "AAError: Failed to append path to memory-saved analytics data. Error: {}".format(e)

        response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        if isinstance(response, str):
            if response.startswith("AAError:"):
                return response

        return True

    @staticmethod
    def newFileUpload():
        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
            AccessAnalytics.analyticsData['fileUploads'] += 1
        except Exception as e:
            return "AAError: Failed to increment file uploads metric. Error: {}".format(e)

        response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        if isinstance(response, str):
            if response.startswith("AAError:"):
                return response
        
        return True

    @staticmethod
    def newFileDeletion():
        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
            AccessAnalytics.analyticsData['fileDeletions'] += 1
        except Exception as e:
            return "AAError: Failed to increment file deletions metric. Error: {}".format(e)

        response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        if isinstance(response, str):
            if response.startswith("AAError:"):
                return response
        
        return True

    @staticmethod
    def newFileDownload():
        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
            AccessAnalytics.analyticsData['fileDownloads'] += 1
        except Exception as e:
            return "AAError: Failed to increment file downloads metric. Error: {}".format(e)

        response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        if isinstance(response, str):
            if response.startswith("AAError:"):
                return response
        
        return True

    @staticmethod
    def newSignin():
        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
            AccessAnalytics.analyticsData['signIns'] += 1
        except Exception as e:
            return "AAError: Failed to increment sign ins metric. Error: {}".format(e)

        response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        if isinstance(response, str):
            if response.startswith("AAError:"):
                return response
        
        return True

    @staticmethod
    def newSignout():
        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
            AccessAnalytics.analyticsData['signOuts'] += 1
        except Exception as e:
            return "AAError: Failed to increment sign outs metric. Error: {}".format(e)

        response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        if isinstance(response, str):
            if response.startswith("AAError:"):
                return response
        
        return True
    
    @staticmethod
    def newPOSTRequest():
        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
            AccessAnalytics.analyticsData['postRequests'] += 1
        except Exception as e:
            return "AAError: Failed to increment post requests metric. Error: {}".format(e)

        response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        if isinstance(response, str):
            if response.startswith("AAError:"):
                return response
        
        return True
        


