import os, sys, json, datetime, copy, uuid, re
from firebase_admin import db, storage, credentials, initialize_app
from dotenv import load_dotenv
load_dotenv()

class FireConn:
    '''A class that manages the admin connection to Firebase via the firebase_admin module.
    
    Explicit permission has to be granted by setting `FireConnEnabled` to `True` in the .env file. `serviceAccountKey.json` file must be in working directory to provide credentials for the connection. Obtain one on the Firebase Console (under Service Accounts > Firebase Admin SDK > Generate new private key).

    Usage:

    ```
    response = FireConn.connect()
    if response != True:
        print("Error in setting up FireConn; error: " + response)
        sys.exit(1)
    ```

    NOTE: This class is not meant to be instantiated. Other services relying on connection via firebase_admin module need to run the `connect` method in this class first. If permission is not granted, dependant services may not be able to operate.
    '''
    connected = False

    @staticmethod
    def checkPermissions():
        return ("FireConnEnabled" in os.environ and os.environ["FireConnEnabled"] == "True")

    @staticmethod
    def connect():
        '''Returns True upon successful connection.'''
        if not FireConn.checkPermissions():
            return "ERROR: Firebase connection permissions are not granted."
        if not os.path.exists("serviceAccountKey.json"):
            return "ERROR: Failed to connect to Firebase. The file serviceAccountKey.json was not found. Please re-read instructions for the Firebase addon."
        else:
            if 'RTDB_URL' not in os.environ:
                return "ERROR: Failed to connect to Firebase. RTDB_URL environment variable not set in .env file. Please re-read instructions for the Firebase addon."
            try:
                ## Firebase
                cred_obj = credentials.Certificate(os.path.join(os.getcwd(), "serviceAccountKey.json"))
                default_app = initialize_app(cred_obj, {
                    'databaseURL': os.environ["RTDB_URL"],
                    'httpTimeout': 5
                })
                FireConn.connected = True
            except Exception as e:
                return "ERROR: Error occurred in connecting to RTDB; error: {}".format(e)
            return True
        
class FireRTDB:
    '''A class to update Firebase Realtime Database (RTDB) references with data.

    Explicit permission has to be granted by setting `FireRTDBEnabled` to `True` in the .env file.

    Usage:
    ```
    if FireRTDB.checkPermissions():
        data = {"name": "John Appleseed"}
        FireRTDB.setRef(data, refPath="/")
        fetchedData = FireRTDB.getRef(refPath="/")
        print(fetchedData) ## same as data defined above
    ```

    Advanced Usage:
    ```
    ## DB translation
    db = {"jobs": {}}
    safeForCloudDB = FireRTDB.translateForCloud(db) ## {"jobs": 0}
    # safeForLocalDB = FireRTDB.translateForLocal(safeForCloudDB) ## {"jobs": {}}
    ```

    `FireRTDB.translateForCloud` and `FireRTDB.translateForLocal` are used to translate data structures for cloud and local storage respectively. This is because Firebase does not allow null objects to be stored in the RTDB. This method converts null objects to a value that can be stored in the RTDB. The following conversions are performed:
    - Converts `{}` to `0` and `[]` to `1` (for cloud storage)
    - Converts `0` to `{}` and `1` to `[]` (for local storage)

    NOTE: This class is not meant to be instantiated. `FireConn.connect()` method must be executed before executing any other methods in this class.
    '''

    @staticmethod
    def checkPermissions():
        '''Returns True if permission is granted, otherwise returns False.'''
        if 'FireRTDBEnabled' in os.environ and os.environ['FireRTDBEnabled'] == 'True':
            return True
        return False

    @staticmethod
    def clearRef(refPath="/"):
        '''Returns True upon successful update. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            return "ERROR: FireRTDB service operation permission denied."
        try:
            ref = db.reference(refPath)
            ref.delete()
        except Exception as e:
            return "ERROR: Error occurred in clearing children at that ref; error: {}".format(e)
        return True

    @staticmethod
    def setRef(data, refPath="/"):
        '''Returns True upon successful update. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            raise Exception("ERROR: FireRTDB service operation permission denied.")
        try:
            ref = db.reference(refPath)
            ref.set(data)
        except Exception as e:
            raise Exception("ERROR: Error occurred in setting data at that ref; error: {}".format(e))
        return True

    @staticmethod
    def getRef(refPath="/"):
        '''Returns a dictionary of the data at the specified ref. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            raise Exception("ERROR: FireRTDB service operation permission denied.")
        data = None
        try:
            ref = db.reference(refPath)
            data = ref.get()
        except Exception as e:
            raise Exception("ERROR: Error occurred in getting data from that ref; error: {}".format(e))
        
        return data
        
    @staticmethod
    def recursiveReplacement(obj, purpose):
        dictValue = {} if purpose == 'cloud' else 0
        dictReplacementValue = 0 if purpose == 'cloud' else {}

        arrayValue = [] if purpose == 'cloud' else 1
        arrayReplacementValue = 1 if purpose == 'cloud' else []

        data = copy.deepcopy(obj)

        for key in data:
            if isinstance(data, list):
                # This if statement forbids the following sub-data-structure: [{}, 1, {}] (this is an example)
                continue

            if isinstance(data[key], dict):
                if data[key] == dictValue:
                    data[key] = dictReplacementValue
                else:
                    data[key] = FireRTDB.recursiveReplacement(data[key], purpose)
            elif isinstance(data[key], list):
                if data[key] == arrayValue:
                    data[key] = arrayReplacementValue
                else:
                    data[key] = FireRTDB.recursiveReplacement(data[key], purpose)
            elif isinstance(data[key], bool):
                continue
            elif isinstance(data[key], int) and purpose == 'local':
                if data[key] == 0:
                    data[key] = {}
                elif data[key] == 1:
                    data[key] = []

        return data
    
    @staticmethod
    def translateForLocal(fetchedData, rootTranslatable=False):
        '''Returns a translated data structure that can be stored locally.'''
        if fetchedData == None:
            return None
        if rootTranslatable:
            if fetchedData == 0:
                return {}
            elif fetchedData == 1:
                return []
            elif not (isinstance(fetchedData, dict) or isinstance(fetchedData, list)):
                return fetchedData
        
        tempData = copy.deepcopy(fetchedData)

        try:
            # Null object replacement
            tempData = FireRTDB.recursiveReplacement(obj=tempData, purpose='local')

            # Further translation here
            
        except Exception as e:
            return "ERROR: Error in translating fetched RTDB data for local system use; error: {}".format(e)
        
        return tempData
    
    @staticmethod
    def translateForCloud(loadedData, rootTranslatable=False):
        '''Returns a translated data structure that can be stored in the cloud.'''
        if loadedData == None:
            return None
        if rootTranslatable:
            if loadedData == {}:
                return 0
            elif loadedData == []:
                return 1
            elif not (isinstance(loadedData, dict) or isinstance(loadedData, list)):
                return loadedData

        tempData = copy.deepcopy(loadedData)

        # Further translation here

        # Null object replacement
        tempData = FireRTDB.recursiveReplacement(obj=tempData, purpose='cloud')

        return tempData