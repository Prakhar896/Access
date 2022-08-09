import os, sys, json, random, subprocess, shutil, uuid, time
import datetime
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
    def generateRandomID(customLength=None):
        if customLength == None:
            randomID = uuid.uuid4().hex

            return randomID
        else:
            options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            randomID = ''
            for i in range(customLength):
                randomID += random.choice(options)

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
            print("Recovery mode will now exit in 3 seconds...")
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
        if subject not in [
            'Access Identity Login Alert', 
            'Access Folder Registered!', 
            'Access Portal OTP', 
            'File Deletion | Access Portal', 
            'File Uploaded | Access Portal',
            'Confirm Email Update | Access Portal',
            'Password Updated | Access Portal',
            'Password Reset Key | Access Portal'
            ]:
            return "AAError: Subject is not valid."
        
        type = ''
        if subject == "Access Identity Login Alert":
            type = 'loginAlert'
        elif subject == 'Access Folder Registered!':
            type = 'folderRegistered'
        elif subject == 'Access Portal OTP':
            type = 'otp'
        elif subject == 'File Deletion | Access Portal':
            type = 'fileDeletionNotif'
        elif subject == 'File Uploaded | Access Portal':
            type = 'fileUploadNotif'
        elif subject == 'Confirm Email Update | Access Portal':
            type = 'emailUpdateConfirmation'
        elif subject == 'Password Updated | Access Portal':
            type = 'passwordUpdated'
        elif subject == 'Password Reset Key | Access Portal':
            type = 'passwordResetKey'
        
        emailID = AccessAnalytics.generateRandomID()

        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
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
    
    @staticmethod
    def newIdentityDeletion():
        try:
            if 'emails' not in AccessAnalytics.analyticsData:
                return "AAError: Likely due to insufficient permissions, a copy of the analytics data was not loaded onto memory. Try enabling AccessAnalytics in the .env file. (emails parameter not found in memory location data)"
            ## Backwards compatibility code
            if 'identityDeletions' not in AccessAnalytics.analyticsData:
                AccessAnalytics.analyticsData['identityDeletions'] = 0
            
            AccessAnalytics.analyticsData['identityDeletions'] += 1
        except Exception as e:
            return "AAError: Failed to increment identity deletions metric. Error: {}".format(e)
        
        response = AccessAnalytics.saveDataToFile(open('analyticsData.txt', 'w'))
        if isinstance(response, str):
            if response.startswith("AAError:"):
                return response
        elif response == False:
            return "AAError: Access Analytics is not given permission to collect data."

        return True
    
    @staticmethod
    def crunchData():
        ### Statistics to calculate:
        #### 1) Number of Requests
        #### 2) Number of Portal Requests
        #### 3) Number of File Uploads
        #### 4) Number of File Deletions
        #### 5) Number of File Downloads
        #### 6) Number of Sign Ins
        #### 7) Number of Sign Outs
        #### 8) Number of POST Requests
        #### 9) Number of GET Requests
        #### 10) Number of API Requests
        #### 11) Number of Assets Requests
        #### 12) Number of unique auth tokens
        #### 13) Number of unique Certification Identification Numbers
        #### EMAILS BREAKDOWN:
        ##### 14) Number of emails sent
        ##### 15) Number of emails of each type of email
        ##### 16) Most frequent email recipient
        #### 17) Number of identities deleted

        if not AccessAnalytics.permissionCheck():
            print("AAError: Insufficient permissions to access analytics data. Try enabling AccessAnalytics in the .env file.")
            return "AAError: Insufficient permissions to access analytics data."

        print("Starting Analysis of data...")
        time.sleep(2)

        response = AccessAnalytics.prepEnvironmentForAnalytics()
        if isinstance(response, str):
            if response.startswith("AAError:"):
                print(response)
                return response
        elif response != True:
            print("AAError: Failed to prepare environment for analytics data. Error: {}".format(response))
            return "AAError: Failed to prepare environment for analytics data."
        
        loadedData = AccessAnalytics.analyticsData

        print()
        print("Analysing requests data...")
        time.sleep(3)

        # Metric 1
        numRequests = len(loadedData["requests"])

        # Metric 2
        numPortalRequests = 0
        for request in loadedData["requests"]:
            if request.startswith("/portal"):
                numPortalRequests += 1
        
        print()
        print("Analysing portal operations...")
        time.sleep(3)

        # Metric 3
        numFileUploads = loadedData["fileUploads"]

        # Metric 4
        numFileDeletions = loadedData["fileDeletions"]

        # Metric 5
        numFileDownloads = loadedData["fileDownloads"]

        # Metric 6
        numSignIns = loadedData["signIns"]

        # Metric 7
        numSignOuts = loadedData["signOuts"]

        # Metric 8
        numPOSTRequests = loadedData["postRequests"]

        # Metric 9
        numGETRequests = len(loadedData["requests"]) - numPOSTRequests
        
        print()
        print("Analysing complex requests...")
        time.sleep(3)

        # Metric 10
        numAPIRequests = 0
        for request in loadedData["requests"]:
            if request.startswith("/api"):
                numAPIRequests += 1
        
        # Metric 11
        numAssetsRequests = 0
        for request in loadedData["requests"]:
            if request.startswith("/assets"):
                numAssetsRequests += 1
        
        # Metric 12
        numUniqueAuthTokens = 0
        authTokens = []
        for request in loadedData["requests"]:
            if request.startswith("/portal/session"):
                path = request.split('/')
                path.pop(0)
                authToken = path[3]
                if authToken not in authTokens:
                    authTokens.append(authToken)
        numUniqueAuthTokens = len(authTokens)
        
        print()
        print("Analysing credentials production and utilisation...")
        time.sleep(3
        )

        # Metric 13
        numUniqueCertificationIdentificationNumbers = 0
        uniqueCertIDs = []
        for request in loadedData["requests"]:
            if request.startswith("/portal/session"):
                path = request.split('/')
                path.pop(0)
                certID = path[2]
                if len(certID) != 20:
                    continue
                if certID not in uniqueCertIDs:
                    uniqueCertIDs.append(certID)
        numUniqueCertificationIdentificationNumbers = len(uniqueCertIDs)

        print()
        print("Analysing electronic mails...")
        time.sleep(2)

        # Metric 14
        numEmailsSent = len(loadedData["emails"])

        # Metric 15
        numEmailsForEachType = {
            "loginAlert": 0,
            "folderRegistered": 0,
            "otp": 0,
            "fileDeletionNotif": 0,
            "fileUploadNotif": 0,
            "emailUpdateConfirmation": 0,
            "passwordUpdated": 0,
            "passwordResetKey": 0
        }

        for emailID in loadedData["emails"]:
            numEmailsForEachType[loadedData["emails"][emailID]["type"]] += 1

        # Metric 16
        recipientAndNumberOfRespectiveEmailsSentToThem = {}

        for emailID in loadedData["emails"]:
            if loadedData["emails"][emailID]["destEmail"] not in recipientAndNumberOfRespectiveEmailsSentToThem:
                recipientAndNumberOfRespectiveEmailsSentToThem[loadedData["emails"][emailID]["destEmail"]] = 0
            
            recipientAndNumberOfRespectiveEmailsSentToThem[loadedData["emails"][emailID]["destEmail"]] += 1

        mostFreqRecipient = ""
        numEmailsSentToFreqRecipient = 0

        for recipient in recipientAndNumberOfRespectiveEmailsSentToThem:
            if recipientAndNumberOfRespectiveEmailsSentToThem[recipient] > numEmailsSentToFreqRecipient:
                mostFreqRecipient = recipient
                numEmailsSentToFreqRecipient = recipientAndNumberOfRespectiveEmailsSentToThem[recipient]

        # Metric 17
        print()
        print("Calculating other metrics...")
        time.sleep(2)

        numIdentityDeletions = 0

        if "identityDeletions" in loadedData:
            numIdentityDeletions = loadedData["identityDeletions"]
        
        print()
        print("Collating report...")
        time.sleep(2)
        ### REPORT CREATION
        reportText = """
------ ACCESS ANALYTICS REPORT ON COLLECTED DATA

This report was automatically generated based on the data collected by the Access Analytics Service which was given permissions to collect said data in the .env file.

There are 5 sections to this report, namely:

    1) Requests Analysis - A breakdown of all the requests sent to the Access System
    2) Portal Requests Analysis - A breakdown of all requests that relate to Access Portal operations such as file uploads, sign ins and more.
    3) Credentials Analysis - A breakdown of the certificate identification numbers and auth tokens in the requests.
    4) Emails Analysis - A breakdown of all the emails sent out to recipients by the Access System.
    5) Other Metrics - Metrics that do not fall under any specific category and are typically identity related operations.

REQUESTS ANALYSIS
-----

Total Requests: {}
Portal Requests: {}
POST Requests: {}
GET Requests: {}
API Requests: {}
Assets Requests: {}

PORTAL REQUESTS ANALYSIS
-----

File Uploads: {}
File Deletions: {}
File Downloads: {}
Sign Ins: {}
Sign Outs: {}

CREDENTIALS ANALYSIS
-----

Unique Auth Tokens: {}
Unique Certificate Identification Numbers: {}

EMAILS ANALYSIS
-----

Total Emails Sent: {}
Total Login Alert Emails: {}
Total Folder Registered Emails: {}
Total OTP Code Emails: {}
Total File Deletion Emails: {}
Total File Upload Emails: {}
Total Email Update Confirmation Emails: {}
Total Password Updated Notification Emails: {}
Total Password Reset Key Emails: {}
Most Frequent Email Recipient: {}, Number of Emails Most Frequent Recipient Recived: {}

OTHER METRICS
-----

Total Access Identity Deletions: {}

--------
That is the end of this automatically generated Access Analytics Report. This report was generated on {}

END OF REPORT
""".format(
    numRequests,
    numPortalRequests,
    numPOSTRequests,
    numGETRequests,
    numAPIRequests,
    numAssetsRequests,
    numFileUploads,
    numFileDeletions,
    numFileDownloads,
    numSignIns,
    numSignOuts,
    numUniqueAuthTokens,
    numUniqueCertificationIdentificationNumbers,
    numEmailsSent,
    numEmailsForEachType["loginAlert"],
    numEmailsForEachType["folderRegistered"],
    numEmailsForEachType["otp"],
    numEmailsForEachType["fileDeletionNotif"],
    numEmailsForEachType["fileUploadNotif"],
    numEmailsForEachType["emailUpdateConfirmation"],
    numEmailsForEachType["passwordUpdated"],
    numEmailsForEachType["passwordResetKey"],
    mostFreqRecipient,
    numEmailsSentToFreqRecipient,
    numIdentityDeletions,
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' UTC' + time.strftime('%z')
)

        print(reportText)

        ## Giving the user the option to save the report as a text file
        print()
        print()
        print("AA: Would you like to save this report as a text file?")
        saveAction = input("Type 'yes' or 'no': ")
        
        if saveAction == "yes":
            print()
            print("AA: Preparing environnment for saving report...")
            time.sleep(2)
            
            try:
                if not os.path.isdir(os.path.join(os.getcwd(), 'analyticsReports')):
                    os.mkdir(os.path.join(os.getcwd(), 'analyticsReports'))
            except Exception as e:
                print("AAError: Failed to make/check existence of reports folder; Error: {}".format(e))
                print("AA: Report could not be saved. Aborting save...")
                return
            
            rel_path = "analyticsReports/aa-report-{}-{}.txt".format(datetime.datetime.now().strftime("%Y%m%dI%H%M%S"), AccessAnalytics.generateRandomID(customLength=7))

            try:
                with open(rel_path, 'w') as f:
                    f.write(reportText)
            except Exception as e:
                print("AAError: Error occurred in saving report into file; Error: {}".format(e))
            
            print()
            print("AA: Report successfully saved at the file at the relative path: {} !".format(rel_path))
            return
        elif saveAction == "no":
            print()
            print("AA: Exiting anaytics...")
            return
        else:
            print()
            print("AAError: Invalid action provided. Exiting analytics...")
            return

    @staticmethod
    def clearDataFile():
        if not os.path.isfile(os.path.join(os.getcwd(), 'analyticsData.txt')):
            return "AAError: Analytics Data file does not exist."
        
        try:
            with open('analyticsData.txt', 'w') as f:
                json.dump(AccessAnalytics.blankAnalyticsObject, f)
        except Exception as e:
            return "AAError: Error in clearing the data file; Error: {}".format(e)
        
        return True

    

