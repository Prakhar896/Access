import os, sys, json, random, subprocess, shutil, uuid, time
import datetime
from dotenv import load_dotenv
from services import Logger
load_dotenv()

class AccessAnalytics:
    analyticsData = {}
    dataFile = "analyticsData.json"
    setup = False

    blankAnalyticsObject = {
        "requests": 0,
        "postRequests": 0,
        "fileUploads": 0,
        "fileDeletions": 0,
        "fileDownloads": 0,
        "fileShares": 0,
        "identityCreations": 0,
        "signIns": 0,
        "signOuts": 0,
        "identityDeletions": 0,
        "emailsSent": 0
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
    def setupEnvironment():
        if not AccessAnalytics.permissionCheck():
            return "AAError: Access Analytics is not enabled and given permission to operate. Set AccessAnalyticsEnabled to True in the .env file to enable Analytics."

        if not os.path.isfile(os.path.join(os.getcwd(), AccessAnalytics.dataFile)):
            with open(AccessAnalytics.dataFile, 'w') as f:
                blankObject = AccessAnalytics.blankAnalyticsObject
                json.dump(blankObject, f)
                AccessAnalytics.analyticsData = blankObject
        else:
            ## Check if file data is damaged
            try:
                fileData = json.load(open(AccessAnalytics.dataFile, 'r'))
            except Exception as e:
                return "AAError: Failed to load data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
            for metric in [x for x in AccessAnalytics.blankAnalyticsObject]:
                if not metric in fileData:
                    return "AAError: analyticsData.json file is damaged ('{}' metric is not present). Please delete the file and run environment prep again.".format(metric)
            AccessAnalytics.analyticsData = fileData
        
        AccessAnalytics.setup = True
        return "AA: Environment prep successful."
    
    @staticmethod
    def analyticsRecoveryMode():
        Logger.log("AA RECOVERYMODE: Analytics recovery mode activated.")
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
            fileData = json.load(open(AccessAnalytics.dataFile, 'r'))
        except Exception as e:
            fileLoadingError = True
            fileLoadingCheck = e
        

        if fileLoadingError:
            print("Issue identified: The system was unable to properly load the AccessAnalytics.dataFile file in JSON form. System Error Note: {}".format(fileLoadingCheck))
            print()
            print("""
            This can occur due to two things:
            1) The file data in AccessAnalytics.dataFile was manually edited in a manner that caused the system's JSON engine to be unable to read the file data in JSON form.
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
                    os.remove(os.path.join(os.getcwd(), AccessAnalytics.dataFile))

                    # Re-write blank data
                    with open(AccessAnalytics.dataFile, 'w') as f:
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
                fileData[metric] = 0
            
            ## Save updates
            try:
                with open(AccessAnalytics.dataFile, 'w') as f:
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
    def loadFromFile():
        if not AccessAnalytics.permissionCheck():
            return "AAError: Access Analytics is not enabled and given permission to operate. Set AccessAnalyticsEnabled to True in the .env file to enable Analytics."

        try:
            with open(AccessAnalytics.dataFile, 'r') as f:
                AccessAnalytics.analyticsData = json.load(f)
        except Exception as e:
            return "AAError: Failed to load data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
        return True

    @staticmethod
    def saveToFile():
        if not AccessAnalytics.permissionCheck():
            # return "AAError: Access Analytics is not enabled and given permission to operate. Set AccessAnalyticsEnabled to True in the .env file to enable Analytics."
            return False
        
        try:
            with open(AccessAnalytics.dataFile, 'w') as f:
                json.dump(AccessAnalytics.analyticsData, f)
        except Exception as e:
            return "AAError: Failed to save data in analytics file in JSON form. File might be damaged.\nError: " + str(e)
        return True

    @staticmethod
    def newRequest():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'requests' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['requests'] = 0
        AccessAnalytics.analyticsData['requests'] += 1

        return AccessAnalytics.saveToFile()

    @staticmethod
    def newFileUpload():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'fileUploads' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['fileUploads'] = 0
        AccessAnalytics.analyticsData['fileUploads'] += 1

        return AccessAnalytics.saveToFile()

    @staticmethod
    def newFileDeletion():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'fileDeletions' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['fileDeletions'] = 0
        AccessAnalytics.analyticsData['fileDeletions'] += 1

        return AccessAnalytics.saveToFile()

    @staticmethod
    def newFileDownload():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'fileDownloads' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['fileDownloads'] = 0
        AccessAnalytics.analyticsData['fileDownloads'] += 1

        return AccessAnalytics.saveToFile()
    
    @staticmethod
    def newFileShare():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'fileShares' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['fileShares'] = 0
        AccessAnalytics.analyticsData['fileShares'] += 1
        
        return AccessAnalytics.saveToFile()
    
    @staticmethod
    def newIdentityCreation():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'identityCreations' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['identityCreations'] = 0
        AccessAnalytics.analyticsData['identityCreations'] += 1
        
        return AccessAnalytics.saveToFile()

    @staticmethod
    def newSignin():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'signIns' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['signIns'] = 0
        AccessAnalytics.analyticsData['signIns'] += 1

        return AccessAnalytics.saveToFile()

    @staticmethod
    def newSignout():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'signOuts' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['signOuts'] = 0
        AccessAnalytics.analyticsData['signOuts'] += 1

        return AccessAnalytics.saveToFile()
    
    @staticmethod
    def newPOSTRequest():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'postRequests' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['postRequests'] = 0
        AccessAnalytics.analyticsData['postRequests'] += 1

        return AccessAnalytics.saveToFile()
    
    @staticmethod
    def newIdentityDeletion():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'identityDeletions' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['identityDeletions'] = 0
        AccessAnalytics.analyticsData['identityDeletions'] += 1
        
        return AccessAnalytics.saveToFile()
    
    @staticmethod
    def newEmailSent():
        if not AccessAnalytics.permissionCheck() or not AccessAnalytics.setup:
            return False
        
        if 'emailsSent' not in AccessAnalytics.analyticsData:
            AccessAnalytics.analyticsData['emailsSent'] = 0
        AccessAnalytics.analyticsData['emailsSent'] += 1
        
        return AccessAnalytics.saveToFile()
    
    @staticmethod
    def crunchData():
        ### Statistics to calculate:
        #### 1) Number of Requests
        #### 2) Number of GET Requests
        #### 3) Number of POST Requests
        #### 4) Number of File Uploads
        #### 5) Number of File Deletions
        #### 6) Number of File Downloads
        #### 7) Number of File Shares
        #### 8) Number of Identity Creations
        #### 9) Number of Sign Ins
        #### 10) Number of Sign Outs
        #### 11) Number of Identity Deletions
        #### 12) Number of Emails Sent

        if not AccessAnalytics.permissionCheck():
            print("AAError: Insufficient permissions to access analytics data. Try enabling AccessAnalytics in the .env file.")
            return "AAError: Insufficient permissions to access analytics data."

        print("Starting Analysis of data...")

        response = AccessAnalytics.setupEnvironment()
        if isinstance(response, str):
            if response.startswith("AAError:"):
                print(response)
                return response
        elif response != True:
            print("AAError: Failed to prepare environment for analytics data. Error: {}".format(response))
            return "AAError: Failed to prepare environment for analytics data."
        
        loadedData = AccessAnalytics.analyticsData

        print()
        print("Analysing...")

        # Metric 1
        numRequests = loadedData["requests"]
        
        # Metrics 2 and 3
        numPOSTRequests = loadedData["postRequests"]
        numGETRequests = loadedData["requests"] - numPOSTRequests

        # Metric 4
        numFileUploads = loadedData["fileUploads"]

        # Metric 5
        numFileDeletions = loadedData["fileDeletions"]

        # Metric 6
        numFileDownloads = loadedData["fileDownloads"]
        
        # Metric 7
        numFileShares = 0
        if "fileShares" in loadedData:
            numFileShares = loadedData["fileShares"]
        
        # Metric 8
        numIdentityCreations = 0
        if "identityCreations" in loadedData:
            numIdentityCreations = loadedData["identityCreations"]

        # Metric 9
        numSignIns = loadedData["signIns"]

        # Metric 10
        numSignOuts = loadedData["signOuts"]

        # Metric 11
        numIdentityDeletions = 0
        if "identityDeletions" in loadedData:
            numIdentityDeletions = loadedData["identityDeletions"]
        
        # Metric 12
        numEmailsSent = 0
        if "emailsSent" in loadedData:
            numEmailsSent = loadedData["emailsSent"]
        
        print()
        print("Collating report...")
        time.sleep(2)
        ### REPORT CREATION
        reportText = """
------ ACCESS ANALYTICS REPORT ON COLLECTED DATA

This report was automatically generated based on the data collected by the Access Analytics Service which was given permissions to collect said data in the .env file.

REQUESTS ANALYSIS
-----

Total Requests: {}
GET Requests: {}
POST Requests: {}

FILE ACCESS ANALYSIS
-----

File Uploads: {}
File Deletions: {}
File Downloads: {}
File Shares: {}

ACCOUNT ANALYSIS
-----

Identity Creations: {}
Sign Ins: {}
Sign Outs: {}
Identity Deletions: {}
Emails Sent: {}

----

Report generated: {}

END OF REPORT
""".format(
    numRequests,
    numGETRequests,
    numPOSTRequests,
    numFileUploads,
    numFileDeletions,
    numFileDownloads,
    numFileShares,
    numIdentityCreations,
    numSignIns,
    numSignOuts,
    numIdentityDeletions,
    numEmailsSent,
    datetime.datetime.now(datetime.timezone.utc).isoformat()
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
            
            rel_path = "analyticsReports/report-{}-{}.txt".format(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dI%H%M%S"), AccessAnalytics.generateRandomID(customLength=7))

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
            
        return

    @staticmethod
    def clearDataFile():
        if not os.path.isfile(os.path.join(os.getcwd(), AccessAnalytics.dataFile)):
            return "AAError: Analytics data file does not exist."
        
        try:
            with open(AccessAnalytics.dataFile, 'w') as f:
                json.dump(AccessAnalytics.blankAnalyticsObject, f)
        except Exception as e:
            return "AAError: Error in clearing the data file; Error: {}".format(e)
        
        return True