import os, sys, json, random, subprocess, shutil
from dotenv import load_dotenv
load_dotenv()

class AccessAnalytics:

    @staticmethod
    def prepEnvironmentForAnalytics():
        if 'AccessAnalyticsEnabled' in os.environ and os.environ['AccessAnalyticsEnabled'] == 'True':
            # Metrics to calculate
            
            if not os.path.isfile(os.path.join(os.getcwd(), 'analyticsData.txt')):
                with open('analyticsData.txt', 'w') as f:
                    plainData = {
                        "emails": {},
                        "requests": [],
                        "fileUploads": 0,
                        "fileDeletions": 0,
                        "signins": 0,
                        "signups": 0
                    }
                    json.dump(plainData, f)
                print("AA: System environment successfully setup for Access Analytics.")
            else:
                data = json.load(open('analyticsData.txt', 'r'))
                errorOccurred = False
                for metric in ['emails', 'requests', 'fileUploads', 'fileDeletions', 'signins', 'signups']:
                    if metric not in data:
                        errorOccurred = True
                        print("AA ERROR: The metric \"{}\" is not in the current analytics data file.".format(metric))
                        action = input("Would you like to do away with the whole file or simply add the metric in with a blank value (type \"delete\" or \"insert\") ")
                        if action == "insert":
                            if metric == 'emails':
                                data[metric] = {}
                            elif metric == 'requests':
                                data[metric] = []
                            else:
                                data[metric] = 0
                            
                            json.dump(data, open('analyticsData.txt', 'w'))
                            print()
                        elif action == "delete":
                            os.remove(os.path.join(os.getcwd(), 'analyticsData.txt'))
                            AccessAnalytics.prepEnvironmentForAnalytics()
                            return
                        else:
                            print("AA Error: Invalid input provided. Aborting preparation...")
                            return
                if errorOccurred:
                    print("AA: Successfully prepped system environment for Access Analytics.")
                else:
                    print("AA: Environment is already prepped for Access Analytics.")
        else:
            print("AA Error: Access Analytics has not been allowed to track data. Set AccessAnalyticsEnabled to True in the .env file to allow AccessAnalytics to operate.")


AccessAnalytics.prepEnvironmentForAnalytics()