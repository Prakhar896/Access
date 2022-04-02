import os, sys, json, random, subprocess, shutil, uuid, time
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

    blankAnalyticsObject = {
        "emails": {},
        "requests": [],
        "fileUploads": 0,
        "fileDeletions": 0,
        "fileDownloads": 0,
        "signIns": 0,
        "signOuts": 0,
        "postRequests": 0
    }

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
                blankObject = AccessAnalytics.blankAnalyticsObject
                json.dump(blankObject, f)
                AccessAnalytics.analyticsData = blankObject
            return "AA: Environment prep successful."
        else:
            ## Check if file data is damaged
            try:
                fileData = json.load(open('analyticsData.txt', 'r'))
            except Exception as e:
                return "AAError: Failed to load data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
            for metric in [x for x in AccessAnalytics.blankAnalyticsObject]:
                if not metric in fileData:
                    return "AAError: analyticsData.txt file is damaged ('{}' metric is not present). Please delete the file and run environment prep again.".format(metric)
            AccessAnalytics.analyticsData = fileData
            return "AA: Environment prep successful."
    
    @staticmethod
    def analyticsRecoveryMode():
        print()
        print()
        print("---------")
        print("ANALYTICS RECOVERY MODE ACTIVATED")
        print()
        print("Running checks to see what went wrong... please wait!")
        print()
        time.sleep(3)

        fileLoadingError = False
        fileLoadingCheck = None

        ## File loading error check
        try:
            fileData = json.load(open('analyticsData.txt', 'r'))
        except Exception as e:
            fileLoadingError = True
            fileLoadingCheck = e
        

        if fileLoadingError:
            print("Issue identified: The system was unable to properly load the 'analyticsData.txt' file in JSON form. System Error Note: {}".format(fileLoadingCheck))
            print()
            print("""
            This can occur due to two things:
            1) The file data in 'analyticsData.txt' was manually edited in a manner that caused the system's JSON engine to be unable to read the file data in JSON form.
            2) The file has somehow corrupted, possibly due to multiple simultaneous read and write operations.
            """)
            print()
            print("Solution: Delete the file and re-write blank analytics data into the file.")
            print("Solution Disadvantages: Possibly, there might be some actual recorded data in the current data file which will be lost as a result of this.")
            print()
            fileLoadSolutionAction = input("Would you like to go forth with this solution? Type 'yes' or 'no': ")
            while fileLoadSolutionAction not in ['yes', 'no']:
                print("Invalid action provided. Please try again.")
                print()
                fileLoadSolutionAction = input("Would you like to go forth with this solution? Type 'yes' or 'no': ")
                continue
            
            if fileLoadSolutionAction == "yes":
                print()
                print("Continuing with solution... please wait a while...")
                time.sleep(3)

                try:
                    os.remove(os.path.join(os.getcwd(), 'analyticsData.txt'))

                    # Re-write blank data
                    with open('analyticsData.txt', 'w') as f:
                        blankObject = AccessAnalytics.blankAnalyticsObject
                        json.dump(blankObject, f)
                        AccessAnalytics.analyticsData = blankObject
                    
                except Exception as e:
                    print("Failed to remove file and re-write data. Error: {}".format(e))
                    print("Recovery Mode was unable to execute the solution for you. Manual system inspection and intervention is required to fix the issue.")
                    sys.exit(1)
                
                print()
                print("Solution was successfully executed. File damage should be repaired.")
                print("------- EXITING ACCESS ANALYTICS RECOVERY MODE...")
                print()
                return
            elif fileLoadSolutionAction == "no":
                print()
                print("Recovery mode will not execute the solution. As a result, manual system inspection and intervention is required to fix the issue.")
                sys.exit(1)
            else:
                print()
                print("Invalid Action Provided. Recovery mode will abort the system now.")
                sys.exit(1)
        
        ## Check metrics in file data
        invalidOrNotPresentMetrics = []
        for metric in [x for x in AccessAnalytics.blankAnalyticsObject]:
            if metric not in fileData:
                invalidOrNotPresentMetrics.append(metric)
                continue
            if metric == "emails":
                if not isinstance(fileData[metric], dict):
                    invalidOrNotPresentMetrics.append(metric)
            elif metric == "requests":
                if not isinstance(fileData[metric], list):
                    invalidOrNotPresentMetrics.append(metric)
            else:
                if not isinstance(fileData[metric], int):
                    invalidOrNotPresentMetrics.append(metric)

        if invalidOrNotPresentMetrics == []:
            print()
            print("Recovery mode was unable to find an error in the analytics data file.")
            print("The file was successfully loaded by recovery mode and all metrics and their respective data types were also checked.")
            print()
            print("The issue you may be facing might be due to other reasons in the system. Manual inspection and intervention in the system might be required.")
            print()
            print("Recovery mode will not exit in 3 seconds...")
            time.sleep(3)
            print("------- EXITING ACCESS ANALYTICS RECOVERY MODE...")
            print()
            return
        
        print()
        print("Issue Identified: The following metric(s) were not present in the data file or had the incorrect data type in the data file.")
        count = 1
        for metric in invalidOrNotPresentMetrics:
            print("{}. '{}'".format(count, metric))
            count += 1
        print()
        print("""
        This can occur due to three things:
        1) The data file was manually edited such that the data type of the metric was no longer its intended type.
        2) The system inadvertently edited the data file to make the change in data type (highly unlikely, unless system code was edited)
        3) The data file was manually edited such that one or more metrics became absent
        """)
        print()
        print("Solution: Add in the metric if it is not present, otherwise change the data type of the metric to the correct data type.")
        print("Solution Disadvantages: The data file may as a result have more key-pairs (due to some being incorrect) or recorded data may be a value of an incorrect key and hence will be lost when it is read by the system.")
        print()
        invalidMetricSolutionAction = input("Would you like to go forth with this solution? Type 'yes' or 'no': ")
        while invalidMetricSolutionAction not in ['yes', 'no']:
            print("Invalid action provided. Please try again.")
            invalidMetricSolutionAction = input("Would you like to go forth with this solution? Type 'yes' or 'no': ")
            continue
        
        if invalidMetricSolutionAction == 'yes':
            print()
            print("Continuing with solution...please wait a while...")
            time.sleep(3)
            print()

            ## Make updates to fileData
            for metric in invalidOrNotPresentMetrics:
                if metric == "emails":
                    fileData[metric] = {}
                elif metric == "requests":
                    fileData[metric] = []
                else:
                    fileData[metric] = 0
            
            ## Save updates
            try:
                with open('analyticsData.txt', 'w') as f:
                    json.dump(fileData, f)
                
                AccessAnalytics.analyticsData = fileData
            except Exception as e:
                print("Failed to add in or change data type of metrics. Error: {}".format(e))
                print("Recovery Mode was unable to execute the solution for you. Manual system inspection and intervention is required to fix the issue.")
                sys.exit(1)
            
            print()
            print("Solution was successfully executed. File damage should be repaired.")
            print("------- EXITING ACCESS ANALYTICS RECOVERY MODE...")
            print()
            return
        elif invalidMetricSolutionAction == "no":
            print()
            print("Recovery mode will not execute the solution. As a result, manual system inspection and intervention is required to fix the issue.")
            sys.exit(1)
            
        sys.exit(1)




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
        


