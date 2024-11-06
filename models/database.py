import os, sys, json, shutil
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from models.utils import *
from models.firebase import *

class DIRepresentable(ABC):
    originRef: Ref
    
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
            data = self.__dict__
            if 'originRef' in data:
                del data['originRef']
        
            return data
        except:
            return {}
    
    def __str__(self) -> str:
        return str(self.represent())
    
class DI:
    '''DatabaseInterface (DI) is a complex central interface managing all database operations.'''
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
                        return response
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
        
        return True
    
    @staticmethod
    def ensureLocalDBFile():
        if not os.path.isfile(os.path.join(os.getcwd(), DI.localFile)):
            with open(DI.localFile, "w") as f:
                json.dump({}, f)
        
        return

    
    @staticmethod
    def efficientDataWrite(payload: dict | None, ref: Ref):
        '''Part of the failover processes of DI. Updates the local copy of the database whenever a different payload at a reference is detected. Efficient data write happens after a successful load of data from the cloud, where the data at the same reference is checked in the local database. If there is no data at the same reference locally or the data is not the same, that specific dictionary object is changed and the local database is written to. This helps to ensure that the most latest possible copy of a database object is retrieved in the future when cloud communication fails and DI turns to the local database to retrieve data from a reference.'''
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
                except KeyError:
                    referenceNotFound = True
                
                if referenceNotFound and payload == None:
                    print("Case 0")
                    return
                elif not referenceNotFound and payload == None:
                    # Data exists at local reference but payload is None
                    dumpRequired = True
                    print("Case 1")
                    targetDataPointer = localData
                    
                    # Anchor on parent ref of target ref and update child ref subscripted on targetDataPointer (thus updating localData)
                    for subscriptIndex in range(len(ref.subscripts) - 1):
                        targetDataPointer = targetDataPointer[ref.subscripts[subscriptIndex]]
                    targetDataPointer[ref.subscripts[-1]] = None
                elif referenceNotFound and payload != None:
                    # Local reference does not exist but payload is not None
                    dumpRequired = True
                    print("Case 2")
                    
                    # Create parent branches, if they don't already exist. For the last subscript, set the payload.
                    targetDataPointer = localData
                    for subscriptIndex in range(len(ref.subscripts)):
                        if subscriptIndex == (len(ref.subscripts) - 1):
                            targetDataPointer[ref.subscripts[subscriptIndex]] = payload
                        elif ref.subscripts[subscriptIndex] not in targetDataPointer:
                            targetDataPointer[ref.subscripts[subscriptIndex]] = {}
                        
                        targetDataPointer = targetDataPointer[ref.subscripts[subscriptIndex]]
                    
                elif targetDataPointer != payload:
                    # Local reference exists but data does not match with the payload
                    dumpRequired = True
                    print("Case 3")
                    targetDataPointer = localData
                    
                    # Anchor on parent ref of target ref and update child ref subscripted on targetDataPointer (thus updating localData)
                    for subscriptIndex in range(len(ref.subscripts) - 1):
                        targetDataPointer = targetDataPointer[ref.subscripts[subscriptIndex]]
                    targetDataPointer[ref.subscripts[-1]] = payload
            
            if dumpRequired:
                with open(DI.localFile, "w") as f:
                    json.dump(localData, f)
                
                print("Dumped data '{}' to '{}'".format(payload, ref))
        except Exception as e:
            print("DI EFFICIENTFAILOVER WARNING: Failed to write data object to ref '{}' for efficient local failover; error: {}".format(ref, e))
    
    @staticmethod
    def loadLocal(ref: Ref = Ref()):
        DI.ensureLocalDBFile()
        
        data = None
        
        try:
            with open(DI.localFile, "r") as f:
                data = json.load(f)
        except Exception as e:
            print("DI LOADLOCAL ERROR: Failed to load JSON data from local file; error: {}".format(e))
            return DIError("DI LOADLOCAL ERROR: Failed to load data from local file.")
        
        try:
            for subscriptIndex in range(len(ref.subscripts)):
                data = copy.deepcopy(data[ref.subscripts[subscriptIndex]])
        except KeyError:
            return None
        except Exception as e:
            print("DI LOADLOCAL ERROR: Failed to retrieve target ref; error: {}".format(e))
            return DIError("DI LOADLOCAL ERROR: Failed to retrieve target ref.")
        
        return data
    
    @staticmethod
    def newUnsyncedRef(ref: Ref):
        for x in DI.unsyncedRefs:
            if x == ref:
                return True
        
        DI.unsyncedRefs.append(ref)
        return True
    
    @staticmethod
    def synchronise():
        '''This method is activated in the event of an unsynchronised state faced by DI. It tries to update Firebase with unsynced data objects, to which references are stored in the memory. If even one of the synchronisations fail, parent functions are discouraged to use Firebase. Otherwise, DI returns to synchronised state and operates normally in a Firebase-first manner.'''
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
                    print("DI SYNC ERROR: Failed to load local ref '{}'; error: {}".format(unsyncedRef, localSave))
                if localSave != None:
                    # Firebase considers None values as removal of the object, so if the unsynced data is not a data removal, translate it for Firebase compatibility
                    localSave = FireRTDB.translateForCloud(localSave, rootTranslatable=True)
                
                res = None
                if localSave == None:
                    res = FireRTDB.clearRef(str(unsyncedRef))
                else:
                    res = FireRTDB.setRef(localSave, str(unsyncedRef))
                
                if res == True:
                    # DI.unsyncedRefs.pop(unsyncedRefIndex)
                    syncedRefs.append(DI.unsyncedRefs[unsyncedRefIndex])
                else:
                    errors = True
            except Exception as e:
                errors = True
                print("DI SYNC ERROR: Failed to sync local ref '{}' to FireRTDB; error: {}".format(unsyncedRef, e))
                
        for ref in syncedRefs:
            DI.unsyncedRefs.remove(ref)
                
        if errors:
            # One or more unsynced references failed to be saved to Firebase, return False to discourage Firebase-first methodology. Sync status remains False
            return False
        else:
            # All unsynced references are synced and Firebase-first can be used safely
            DI.syncStatus = True
            return True

    @staticmethod
    def load(ref: Ref = Ref()):
        DI.synchronise()
        
        # Check if Firebase is enabled
        if FireRTDB.checkPermissions():
            # Cloud enabled
            if not FireConn.connected:
                print("DI LOAD WARNING: FireRTDB is enabled but Firebase connection is not established; falling back on local load.")
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
            print("DI LOAD WARNING: Failed to load from FireRTDB; error: '{}'. Falling back to local...".format(e))
            return DI.loadLocal(ref)
    
    @staticmethod
    def save(payload, ref: Ref = Ref()):
        DI.efficientDataWrite(payload, ref)
        DI.synchronise()
        
        # Check if Firebase is enabled
        if not FireRTDB.checkPermissions():
            return True
        if not FireConn.connected:
            print("DI SAVE WARNING: Save only persisted locally; FireRTDB enabled but connection is not established.")
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
                print("DI SAVE WARNING: Save only persisted locally; FireRTDB save failed.")
            
        except Exception as e:
            DI.syncStatus = False
            DI.newUnsyncedRef(ref)
            print("DI SAVE WARNING: Save only persisted locally; error in FireRTDB save: {}".format(e))
        
        return True