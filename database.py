import os, sys, json, shutil
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from services import Logger
from utils import *
from firebase import *

class DIRepresentable(ABC):
    '''
    `DIRepresentable` is an Abstract Base Class (ABC) that can be sub-classed to represent database models.
    
    The following methods must be implemented in the subclass:
    - `rawLoad(data: Dict[str, Any]) -> 'DIRepresentable'`: Static method to load raw data into an instance of the subclass.
    - `load(**params: Any) -> 'DIRepresentable | list[DIRepresentable]'`: Static method to load data into an instance of the subclass.
    - `save() -> bool`: Instance method to save the model instance, returning a success status.
    
    The following methods are recommended to be implemented (default implementations provided):
    - `ref(*params: tuple[str]) -> Ref`: Static method to create a reference object.
    - `represent() -> Dict[str, Any]`: Instance method to represent the model instance as a dictionary.
    
    The following methods are optional to implement in the subclass (default implementations provided):
    - `destroy()`: Instance method to destroy the model instance.
    - `reload()`: Instance method to reload the model instance from the database.
    
    Example usage:
    ```python
    class Account(DIRepresentable):
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age
            self.originRef = self.ref("accounts", self.name)
            
        @staticmethod
        def rawLoad(data: Dict[str, Any]) -> 'Account':
            return Account(data['name'], data['age'])
        
        @staticmethod
        def load(name: str) -> 'Account':
            data = DI.load(Account.ref("accounts", name))
            if isinstance(data, DIError):
                return data
            if data == None:
                return None
            return Account.rawLoad(data)
        
        def save(self) -> bool:
            return DI.save(self.represent(), self.originRef)
        
        def destroy(self):
            return DI.save(None, self.originRef)
    
    john = Account.load("john")
    if john == None:
        john = Account("John Doe", 25)
        john.save()
    print(john)
    ```
    '''
    originRef: Ref
    
    @staticmethod
    @abstractmethod
    def rawLoad(data: Dict[str, Any]) -> 'DIRepresentable':
        """Static method to load raw data into an instance of the subclass."""
        pass
    
    @staticmethod
    @abstractmethod
    def load(**params: Any) -> 'DIRepresentable | list[DIRepresentable]':
        """Static method to load data into an instance of the subclass."""
        pass
    
    @abstractmethod
    def save(self) -> bool:
        """Instance method to save the model instance, returning a success status."""
        pass
    
    @staticmethod
    def ref(*params: tuple[str]) -> Ref:
        return Ref(*params)
    
    def represent(self) -> Dict[str, Any]:
        """Instance method to represent the model instance as a dictionary."""
        try:
            data = copy.deepcopy(self.__dict__)
            if 'originRef' in data:
                del data['originRef']
        
            return data
        except:
            return {}
        
    def destroy(self):
        """Instance method to destroy the model instance."""
        return DI.save(None, self.originRef)
    
    def reload(self):
        """Instance method to reload the model instance from the database."""
        
        data = DI.load(self.originRef)
        if isinstance(data, DIError):
            raise Exception("DIR RELOAD ERROR: DIError occurred: {}".format(data))
        if data == None:
            raise Exception("DIR RELOAD ERROR: No data found at reference '{}'.".format(self.originRef))
        if not isinstance(data, dict):
            raise Exception("DIR RELOAD ERROR: Unexpected DI load response format; response: {}".format(data))
        
        self.__dict__.update(self.rawLoad(data).__dict__)
        return True
    
    def __str__(self) -> str:
        return str(self.represent())
    
class DI:
    '''
    **DatabaseInterface (DI) is a complex central interface managing all database operations.**
    
    DI is designed to be a centralised database interface that can be used to interact with a local database and a cloud database (Firebase Realtime Database).
    
    DI is recommended to be used with the `DIRepresentable` abstract class, which is an abstract class which can be sub-classed to represent database models.
    
    Inputs and outputs through DI are almost exclusively dictionaries, though raw values can also be used.
    
    DI features a comprehensive set of failover and synchronisation strategies to ensure data integrity and availability.
    
    DI incorporates referential data handling; what this means:
    - Data objects are considered to be at a reference (Ref) in the database.
    - Example reference: `accounts/john` --> Could be a reference to the account data of a user named John. Example JSON structure where this ref is valid: `{"accounts": {"john": {"name": "John Doe", "age": 25}}}`
    - References are used to load and save data objects. This allows for a structured and organised database.
    - This approach also improves memory efficiency, so that only the required data is loaded and saved.
    
    How DI works:
    1. Setup: DI is initialised with a local database file and a failover strategy. In the event of a `comprehensive` `DI_FAILOVER_STRATEGY`, the entire cloud database is copied to the local database.
    2. Load: Retrieve data objects at a given reference. If Firebase is enabled, data is loaded from Firebase and written to the local database. If Firebase is not enabled, data is loaded from the local database.
    3. Save: Save data objects at a given reference. If Firebase is enabled, data is saved to Firebase and written to the local database. If Firebase is not enabled, data is saved to the local database.
    
    In the event of a desync with Firebase, DI will remember all the references which haven't been updated in Firebase. During any load and save operation, DI will try to synchronise these references with Firebase, but will fall back to the local database if synchronisation fails.
    
    Retrieve the synchronised status of DI with `DI.syncStatus`. You can configure the failover strategy by updating `DI.failoverStrategy` to `comprehensive` or `efficient`, or with the `DI_FAILOVER_STRATEGY` environment variable. The default is `comprehensive`.
    
    DI is designed to be a robust and reliable database interface for small to medium scale applications.
    '''
    localFile = "database.json"
    failoverStrategy = "comprehensive" if not ('DI_FAILOVER_STRATEGY' in os.environ and os.environ.get('DI_FAILOVER_STRATEGY') == 'efficient') else 'efficient' # "comprehensive" or "efficient"
    syncStatus = True
    unsyncedRefs: List[Ref] = []
    
    @staticmethod
    def setup():
        DI.ensureLocalDBFile()
        
        if FireRTDB.checkPermissions():
            try:
                if not FireConn.connected:
                    print("DI-FIRECONN: Firebase connection not established. Attempting to connect...")
                    response = FireConn.connect()
                    if response != True:
                        print("DI-FIRECONN: Failed to connect to Firebase. Aborting setup.")
                        return DIError("DI-FIRECONN ERROR: {}".format(response))
                    else:
                        print("DI-FIRECONN: Firebase connection established. Firebase RTDB is enabled.")
                else:
                    print("DI: Firebase RTDB is enabled.")
            except Exception as e:
                print("DI-FIRECONN ERROR: " + str(e))
                return DIError("DI-FIRECONN ERROR: {}".format(e))
            
            if DI.failoverStrategy == "comprehensive":
                # Copy cloud database to local
                try:
                    data = FireRTDB.translateForLocal(FireRTDB.getRef())
                    if data == None:
                        data = {}
                    with open(DI.localFile, "w") as f:
                        json.dump(data, f)
                except Exception as e:
                    return DIError("DI SETUP ERROR: Failed to make a comprehensive copy of FireRTDB data locally. Error: {}".format(e))
        
        print("DI: Setup complete.")
        return True
    
    @staticmethod
    def ensureLocalDBFile():
        '''
        Creates a `DI.localFile` if it does not exist.
        '''
        if not os.path.isfile(os.path.join(os.getcwd(), DI.localFile)):
            with open(DI.localFile, "w") as f:
                json.dump({}, f)
        
        return

    
    @staticmethod
    def efficientDataWrite(payload: dict | None, ref: Ref):
        '''
        Part of the efficient failover processes of DI. Also used to write data to the local database.
        
        Updates the local copy of the database whenever a different payload at a reference is detected.
        
        Efficient data write happens after a successful load of data from the cloud, where the data at the same reference is checked in the local database.
        
        If there is no data at the same reference locally or the data is not the same, that specific dictionary object is changed and the local database is written to.
        
        This helps to ensure that the most latest possible copy of a database object is retrieved in the future when cloud communication fails and DI turns to the local database to retrieve data from a reference.
        
        The failover strategy can be set to "comprehensive" or "efficient" by setting the environment variable `DI_FAILOVER_STRATEGY` to "comprehensive" or "efficient".
        - Comprehensive: The entire database is copied from the cloud to the local database during setup.
        - Efficient (default): Is active even during `comprehensive` setup. As data is loaded from Firebase, the local copy is kept up to date in the event of a desync to produce the most recent available data for system integrity.
        
        Returns `None`.
        '''
        DI.ensureLocalDBFile()
        
        dumpRequired = False
        try:
            localData = None
            with open(DI.localFile, "r") as f:
                localData = json.load(f)
            
            if len(ref.subscripts) == 0:
                # Root ref
                dumpRequired = True
                if payload == None:
                    localData = {}
                elif localData != payload:
                    localData = payload
            else:
                # Non-root ref
                targetDataPointer = localData
                referenceNotFound = False
                try:
                    for subscriptIndex in range(len(ref.subscripts)):
                        targetDataPointer = targetDataPointer[ref.subscripts[subscriptIndex]]
                        if targetDataPointer == None:
                            referenceNotFound = True
                            break
                except KeyError:
                    referenceNotFound = True
                
                if referenceNotFound and payload == None:
                    # print("Case 0")
                    return
                elif not referenceNotFound and payload == None:
                    # Data exists at local reference but payload is None
                    dumpRequired = True
                    # print("Case 1")
                    targetDataPointer = localData
                    
                    # Anchor on parent ref of target ref and update child ref subscripted on targetDataPointer (thus updating localData)
                    for subscriptIndex in range(len(ref.subscripts) - 1):
                        targetDataPointer = targetDataPointer[ref.subscripts[subscriptIndex]]
                    targetDataPointer[ref.subscripts[-1]] = None
                elif referenceNotFound and payload != None:
                    # Local reference does not exist but payload is not None
                    dumpRequired = True
                    # print("Case 2")
                    
                    # Create parent branches, if they don't already exist. For the last subscript, set the payload.
                    targetDataPointer = localData
                    for subscriptIndex in range(len(ref.subscripts)):
                        if subscriptIndex == (len(ref.subscripts) - 1):
                            targetDataPointer[ref.subscripts[subscriptIndex]] = payload
                        elif ref.subscripts[subscriptIndex] not in targetDataPointer or targetDataPointer[ref.subscripts[subscriptIndex]] == None:
                            targetDataPointer[ref.subscripts[subscriptIndex]] = {}
                        
                        targetDataPointer = targetDataPointer[ref.subscripts[subscriptIndex]]
                    
                elif targetDataPointer != payload:
                    # Local reference exists but data does not match with the payload
                    dumpRequired = True
                    # print("Case 3")
                    targetDataPointer = localData
                    
                    # Anchor on parent ref of target ref and update child ref subscripted on targetDataPointer (thus updating localData)
                    for subscriptIndex in range(len(ref.subscripts) - 1):
                        targetDataPointer = targetDataPointer[ref.subscripts[subscriptIndex]]
                    targetDataPointer[ref.subscripts[-1]] = payload
            
            if dumpRequired:
                with open(DI.localFile, "w") as f:
                    json.dump(localData, f)
                
                # print("Dumped data '{}' to '{}'".format(payload, ref))
        except Exception as e:
            Logger.log("DI EFFICIENTFAILOVER WARNING: Failed to write data object to ref '{}' for efficient local failover; error: {}".format(ref, e))
    
    @staticmethod
    def loadLocal(ref: Ref = Ref()):
        '''
        Attempts to load data at a given reference (Ref) from the local database (DI.localFile).
        
        If the reference is not found, the function returns `None`.
        
        Otherwise, `Ref.subscripts` are iterated through to retrieve the target data object.
        
        Returns the data object. Can also return `DIError` or `None`. `None` represents that there is no data at the given reference.
        '''
        DI.ensureLocalDBFile()
        
        data = None
        
        try:
            with open(DI.localFile, "r") as f:
                data = json.load(f)
        except Exception as e:
            return DIError("DI LOADLOCAL ERROR: Failed to load JSON data from file; error: {}".format(e))
        
        try:
            for subscriptIndex in range(len(ref.subscripts)):
                data = copy.deepcopy(data[ref.subscripts[subscriptIndex]])
        except KeyError:
            return None
        except Exception as e:
            return DIError("DI LOADLOCAL ERROR: Failed to retrieve target ref; error: {}".format(e))
        
        return data
    
    @staticmethod
    def newUnsyncedRef(ref: Ref):
        '''
        Stores the reference to an updated data object in `DI.unsyncedRefs` for future synchronisation.
        
        If the ref is already in the list, the function returns `True` immediately.
        '''
        for x in DI.unsyncedRefs:
            if x == ref:
                return True
        
        DI.unsyncedRefs.append(ref)
        Logger.log("DI NEWUNSYNCEDREF WARNING: New unsynced ref added: '{}'".format(ref))
        return True
    
    @staticmethod
    def synchronise():
        '''
        **Only for Firebase-enabled DI.**
        
        This method is activated in the event of an unsynchronised state faced by DI.
        
        It tries to update Firebase with unsynced data objects, to which references are stored in the memory.
        
        If even one of the synchronisations fail, parent functions are discouraged to use Firebase.
        
        Otherwise, DI returns to synchronised state and operates normally in a Firebase-first manner.
        
        Returns `True` if synchronisation is successful, `False` otherwise.
        '''
        if DI.syncStatus:
            return True
        
        if not (FireRTDB.checkPermissions() and FireConn.connected):
            return False
        
        errors = False
        syncedRefs = []
        for unsyncedRefIndex in range(len(DI.unsyncedRefs)):
            # Iterate through unsynced references and try to write their data to Firebase
            unsyncedRef = DI.unsyncedRefs[unsyncedRefIndex]
            try:
                localSave = DI.loadLocal(unsyncedRef)
                if isinstance(localSave, DIError):
                    Logger.log("DI SYNC ERROR: Failed to load local ref '{}'; error: {}".format(unsyncedRef, localSave))
                if localSave != None:
                    # Firebase considers None values as removal of the object, so if the unsynced data is not a data removal, translate it for Firebase compatibility
                    localSave = FireRTDB.translateForCloud(localSave, rootTranslatable=True)
                
                res = None
                if localSave == None:
                    res = FireRTDB.clearRef(str(unsyncedRef))
                else:
                    res = FireRTDB.setRef(localSave, str(unsyncedRef))
                
                if res == True:
                    syncedRefs.append(DI.unsyncedRefs[unsyncedRefIndex])
                else:
                    errors = True
            except Exception as e:
                errors = True
                Logger.log("DI SYNC ERROR: Failed to sync local ref '{}' to FireRTDB; error: {}".format(unsyncedRef, e))
                
        for ref in syncedRefs:
            DI.unsyncedRefs.remove(ref)
                
        if errors:
            # One or more unsynced references failed to be saved to Firebase, return False to discourage Firebase-first methodology. Sync status remains False
            return False
        else:
            # All unsynced references are synced and Firebase-first can be used safely
            DI.syncStatus = True
            Logger.log("DI SYNC: All unsynced refs synced to Firebase.")
            return True

    @staticmethod
    def load(ref: Ref = Ref()):
        '''
        Load data from the database at a given reference (Ref). If no reference is provided, the data at the root will be loaded.
        
        In the event of desync state, `DI.synchronise` will be used to sync first.
        
        If Firebase is enabled, the load strategy will be as follows:
        - Fetch data from Firebase with `FireRTDB.getRef`
        - Perform data translation with `FireRTDB.translateForLocal` with root translation on
        - Write the data to the local database with `DI.efficientDataWrite` (efficient failover strategy)
        - Return the data
        
        If Firebase is not enabled, the data will be loaded from the local database with `DI.loadLocal`.
        
        In the event of a desync state, the local database will be used for data retrieval.
        
        Returns the data object. Can also return `DIError` or `None`. `None` represents that there is no data at the given reference.
        '''
        DI.synchronise()
        
        # Check if Firebase is enabled
        if FireRTDB.checkPermissions():
            # Cloud enabled
            if not FireConn.connected:
                Logger.log("DI LOAD WARNING: FireRTDB is enabled but Firebase connection is not established; falling back on local load.")
                return DI.loadLocal(ref)
            elif not DI.syncStatus:
                # Unsync-ed state, unsafe for FB operations
                return DI.loadLocal(ref)
        else:
            # No cloud
            return DI.loadLocal(ref)
        
        ## Retrieve data from Firebase
        try:
            data = FireRTDB.translateForLocal(FireRTDB.getRef(str(ref)), rootTranslatable=True)
            DI.efficientDataWrite(data, ref)
            
            return data
        except Exception as e:
            Logger.log("DI LOAD WARNING: Failed to load from FireRTDB; error: '{}'. Falling back to local...".format(e))
            return DI.loadLocal(ref)
    
    @staticmethod
    def save(payload, ref: Ref = Ref()):
        '''
        Save a payload to the database at a given reference (Ref). If no reference is provided, the payload will be written at the root.
        
        In the event of desync state, `DI.synchronise` will be used to sync first.
        
        Local save is conducted by `DI.efficientDataWrite`.
        
        In the event of FireRTDB being enabled but desync state, the reference will be stored in `DI.unsyncedRefs` for future synchronisation.
        
        Otherwise, the payload will be translated with `FireRTDB.translateForCloud` with root translation on.
        
        The translated payload will be written to the reference with `FireRTDB.setRef`. If the payload is None, the reference will be cleared with `FireRTDB.clearRef`.
        
        If the save operation fails, the desync state will be set and the reference will be stored in `DI.unsyncedRefs`.
        
        Returns `True` almost exclusively.
        '''
        DI.efficientDataWrite(payload, ref)
        DI.synchronise()
        
        # Check if Firebase is enabled
        if not FireRTDB.checkPermissions():
            return True
        if not FireConn.connected:
            Logger.log("DI SAVE WARNING: Save only persisted locally; FireRTDB enabled but connection is not established.")
            return True
        if not DI.syncStatus:
            # Unsync-ed state, unsafe for FB operations
            DI.newUnsyncedRef(ref)
            return True
        
        ## Firebase enabled and connected
        try:
            res = None
            if payload == None:
                res = FireRTDB.clearRef(str(ref))
            else:
                res = FireRTDB.setRef(FireRTDB.translateForCloud(payload, rootTranslatable=True), str(ref))
            
            if res != True:
                DI.syncStatus = False
                DI.newUnsyncedRef(ref)
                Logger.log("DI SAVE WARNING: Save only persisted locally; FireRTDB save failed.")
            
        except Exception as e:
            DI.syncStatus = False
            DI.newUnsyncedRef(ref)
            Logger.log("DI SAVE WARNING: Save only persisted locally; error in FireRTDB save: {}".format(e))
        
        return True