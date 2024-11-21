from uuid import uuid4
from typing import List, Dict, Any
from database import *
from services import Universal
from utils import Ref

class Identity(DIRepresentable):
    def __init__(self, username: str, email: str, password: str, lastLogin: str, authToken: str, emailVerification: 'EmailVerification'=None, created: str=None, resetKey: str=None, resetDispatch: str=None, auditLogs: 'Dict[str, AuditLog]'={}, files: 'Dict[str, File]'={}, id: str=None) -> None:
        if id == None:
            id = uuid4().hex
        if emailVerification == None:
            emailVerification = EmailVerification(id)
        if created == None:
            created = Universal.utcNowString()
        
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.lastLogin = lastLogin
        self.authToken = authToken
        self.emailVerification = emailVerification
        self.created = created
        self.resetKey = resetKey
        self.resetDispatch = resetDispatch
        self.auditLogs = auditLogs
        self.files = files
        self.originRef = Identity.ref(id)
        
        self.auditLogsLoaded = False
        self.filesLoaded = False
        
    @staticmethod
    def rawLoad(data: dict, loadAuditLogs=False, loadFiles=False) -> 'Identity':
        requiredParams = ['username', 'email', 'password', 'lastLogin', 'authToken', 'emailVerification', 'created', 'resetKey', 'resetDispatch', 'id']
        for reqParam in requiredParams:
            if reqParam not in data:
                if reqParam in ['emailVerification']:
                    data[reqParam] = {}
                else:
                    data[reqParam] = None
        
        emailVerification = data['emailVerification']
        if isinstance(emailVerification, dict):
            emailVerification = EmailVerification.rawLoad(data['emailVerification'], data['id'])
        else:
            emailVerification = EmailVerification(data['id'])
        
        account = Identity(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            lastLogin=data['lastLogin'],
            authToken=data['authToken'],
            emailVerification=emailVerification,
            created=data['created'],
            resetKey=data['resetKey'],
            resetDispatch=data['resetDispatch'],
            id=data['id']
        )
        
        if loadAuditLogs:
            account.getAuditLogs()
        if loadFiles:
            account.getFiles()
        
        return account
    
    @staticmethod
    def load(id=None, username=None, email=None, authToken=None, withAuditLogs=False, withFiles=False) -> 'Identity | List[Identity] | None':
        if id == None:
            data = DI.load(Ref("accounts"))
            if data == None:
                return None
            if isinstance(data, DIError):
                raise Exception("IDENTITY LOAD ERROR: DIError occurred: {}".format(data))
            if not isinstance(data, dict):
                raise Exception("IDENTITY LOAD ERROR: Failed to load dictionary accounts data; response: {}".format(data))

            identities: Dict[str, Identity] = {}
            for id in data:
                if isinstance(data[id], dict):
                    identities[id] = Identity.rawLoad(data[id], loadAuditLogs=withAuditLogs, loadFiles=withFiles)
            
            if username == None and email == None and authToken == None:
                return list(identities.values())
            
            for identityID in identities:
                targetIdentity = identities[identityID]
                if username != None and targetIdentity.username == username:
                    return targetIdentity
                elif email != None and targetIdentity.email == email:
                    return targetIdentity
                elif authToken != None and targetIdentity.authToken == authToken:
                    return targetIdentity
            
            return None
        else:
            data = DI.load(Identity.ref(id))
            if isinstance(data, DIError):
                raise Exception("IDENTITY LOAD ERROR: DIError occurred: {}".format(data))
            if data == None:
                return None
            if not isinstance(data, dict):
                raise Exception("IDENTITY LOAD ERROR: Unexpected DI load response format; response: {}".format(data))
            
            return Identity.rawLoad(data, loadAuditLogs=withAuditLogs, loadFiles=withFiles)
        
    def represent(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "lastLogin": self.lastLogin,
            "authToken": self.authToken,
            "emailVerification": self.emailVerification.represent(),
            "created": self.created,
            "resetKey": self.resetKey,
            "resetDispatch": self.resetDispatch
        }
        
    def save(self):
        convertedData = self.represent()
        
        return DI.save(convertedData, self.originRef)
    
    def getAuditLogs(self):
        accountLogs = AuditLog.load(accountID=self.id)
        if accountLogs == None:
            self.auditLogs = {}
            self.auditLogsLoaded = True
            return True
        if not isinstance(accountLogs, list):
            raise Exception("IDENTITY GETAUDITLOGS ERROR: Unexpected response format; response: {}".format(accountLogs))

        self.auditLogs = {log.id: log for log in accountLogs}
        self.auditLogsLoaded = True
        return True
    
    def getFiles(self):
        accountFiles = File.load(accountID=self.id)
        if accountFiles == None:
            self.files = {}
            self.filesLoaded = True
            return True
        if not isinstance(accountFiles, list):
            raise Exception("IDENTITY GETFILES ERROR: Unexpected response format; response: {}".format(accountFiles))
        
        self.files = {file.id: file for file in accountFiles}
        self.filesLoaded = True
        return True
    
    def deleteAuditLog(self, logID):
        '''Deletes an audit log from the account's audit logs.'''
        if logID not in self.auditLogs:
            raise Exception("IDENTITY DELETEAUDITLOG ERROR: Log ID '{}' not found in account's audit logs.".format(logID))
        
        deletion = self.auditLogs[logID].destroy()
        if deletion != True:
            raise Exception("IDENTITY DELETEAUDITLOG ERROR: Failed to delete audit log; response: {}".format(deletion))
        del self.auditLogs[logID]
        
        return True
    
    def deleteFile(self, fileID):
        '''Deletes a file from the account's files.'''
        if fileID not in self.files:
            raise Exception("IDENTITY DELETEFILE ERROR: File ID '{}' not found in account's files.".format(fileID))
        
        deletion = self.files[fileID].destroy()
        if deletion != True:
            raise Exception("IDENTITY DELETEFILE ERROR: Failed to delete file; response: {}".format(deletion))
        del self.files[fileID]
        
        return True
    
    @staticmethod
    def ref(id):
        return Ref("accounts", id)
    
class EmailVerification(DIRepresentable):
    def __init__(self, accountID: str, verified: bool=False, otpCode: str=None, dispatchTimestamp: str=None) -> None:
        self.accountID = accountID
        self.verified = verified
        self.otpCode = otpCode
        self.dispatchTimestamp = dispatchTimestamp
        self.originRef = EmailVerification.ref(accountID)
        
    @staticmethod
    def rawLoad(data: Dict[str, Any], accountID: str) -> 'EmailVerification':
        requiredParams = ['verified', 'otpCode', 'dispatchTimestamp']
        for reqParam in requiredParams:
            if reqParam not in data:
                if reqParam == 'verified':
                    data[reqParam] = False
                else:
                    data[reqParam] = None
        
        return EmailVerification(
            accountID=accountID,
            verified=data['verified'] == "True",
            otpCode=data['otpCode'],
            dispatchTimestamp=data['dispatchTimestamp']
        )
    
    @staticmethod
    def load(accountID: str) -> 'EmailVerification | None':
        data = DI.load(EmailVerification.ref(accountID))
        if data == None:
            return None
        if isinstance(data, DIError):
            raise Exception("EMAILVERIFICATION LOAD ERROR: DIError occurred: {}".format(data))
        if not isinstance(data, dict):
            raise Exception("EMAILVERIFICATION LOAD ERROR: Unexpected DI load response format; response: {}".format(data))
        
        return EmailVerification.rawLoad(data, accountID)
    
    def represent(self) -> Dict[str, Any]:
        return {
            "verified": str(self.verified),
            "otpCode": self.otpCode,
            "dispatchTimestamp": self.dispatchTimestamp
        }
    
    def save(self) -> bool:
        convertedData = self.represent()
        
        return DI.save(convertedData, self.originRef)
    
    def destroy(self):
        return DI.save({}, self.originRef)
    
    @staticmethod
    def ref(accountID: str) -> Ref:
        return Ref("accounts", accountID, "emailVerification")
    
class AuditLog(DIRepresentable):
    def __init__(self, accountID: str, event: str, text: str, id: str=None, timestamp: str=None) -> None:
        if id == None:
            id = uuid4().hex
        if timestamp == None:
            timestamp = Universal.utcNowString()
        
        self.id = id
        self.accountID = accountID
        self.timestamp = timestamp
        self.event = event
        self.text = text
        self.originRef = AuditLog.ref(id)
        
    @staticmethod
    def rawLoad(data: dict) -> 'AuditLog':
        requiredParams = ['event', 'text', 'id', 'accountID', 'timestamp']
        for reqParam in requiredParams:
            if reqParam not in data:
                data[reqParam] = None
        
        return AuditLog(
            accountID=data['accountID'],
            event=data['event'],
            text=data['text'],
            id=data['id'],
            timestamp=data['timestamp']
        )
    
    @staticmethod
    def load(id=None, accountID=None) -> 'AuditLog | List[AuditLog] | None':
        if id != None:
            # Load a specific audit log
            log = DI.load(AuditLog.ref(id))
            if isinstance(log, DIError):
                raise Exception("AUDITLOG LOAD ERROR: DIError: {}".format(log))
            if log == None:
                return None
            if not isinstance(log, dict):
                raise Exception("AUDITLOG LOAD ERROR: Unexpected DI log load response format; response: {}".format(log))
            
            return AuditLog.rawLoad(log)
        elif accountID != None:
            # Load all audit logs for the targeted account
            logs = DI.load(Ref("auditLogs"))
            if isinstance(logs, DIError):
                raise Exception("AUDITLOG LOAD ERROR: DIError: {}".format(logs))
            if logs == None:
                return None
            if not isinstance(logs, dict):
                return Exception("AUDITLOG LOAD ERROR: Unexpected DI logs load response format; response: {}".format(logs))
            
            accountLogs = []
            for logData in logs.values():
                if isinstance(logData, dict):
                    if logData['accountID'] == accountID:
                        accountLogs.append(AuditLog.rawLoad(logData))
            
            return accountLogs
        else:
            # Load all audit logs
            logs = DI.load(Ref("auditLogs"))
            if isinstance(logs, DIError):
                raise Exception("AUDITLOG LOAD ERROR: DIError: {}".format(logs))
            if logs == None:
                return None
            if not isinstance(logs, dict):
                return Exception("AUDITLOG LOAD ERROR: Unexpected DI logs load response format; response: {}".format(logs))
            
            return [AuditLog.rawLoad(logData) for logData in logs.values() if isinstance(logData, dict)]

    def save(self, checkIntegrity=True) -> bool:
        convertedData = self.represent()
        
        if checkIntegrity:
            targetAccount = DI.load(Identity.ref(self.accountID))
            if isinstance(targetAccount, DIError):
                raise Exception("AUDITLOG SAVE ERROR: DIError: {}".format(targetAccount))
            if targetAccount == None:
                raise Exception("AUDITLOG SAVE ERROR: Account not found.")
            if not isinstance(targetAccount, dict):
                raise Exception("AUDITLOG SAVE ERROR: Unexpected DI account load response format; response: {}".format(targetAccount))
        
        return DI.save(convertedData, self.originRef)
    
    def linkTo(self, user: Identity):
        user.auditLogs[self.id] = self
        return True
    
    @staticmethod
    def ref(logID) -> Ref:
        return Ref("auditLogs", logID)
    
class File(DIRepresentable):
    def __init__(self, accountID: str, name: str, blocked: bool=False, sharing: 'FileSharing'=None, id: str=None, uploadedTimestamp: str=None, lastUpdate: str=None) -> None:
        if id == None:
            id = uuid4().hex
        if uploadedTimestamp == None:
            uploadedTimestamp = Universal.utcNowString()
        if sharing == None:
            sharing = FileSharing(id)
        
        self.id = id
        self.accountID = accountID
        self.name = name
        self.blocked = blocked
        self.sharing = sharing
        self.uploadedTimestamp = uploadedTimestamp
        self.lastUpdate = lastUpdate
        self.originRef = File.ref(id)
        
    @staticmethod
    def getExtFrom(fileName: str):
        return fileName.split(".")[-1]
        
    @staticmethod
    def rawLoad(data: Dict[str, Any]) -> 'File':
        requiredParams = ['accountID', 'name', 'blocked', 'sharing', 'id', 'uploadedTimestamp', 'lastUpdate']
        for reqParam in requiredParams:
            if reqParam not in data:
                if reqParam in ['sharing']:
                    data[reqParam] = {}
                else:
                    data[reqParam] = None
        
        sharing = data['sharing']
        if isinstance(sharing, dict):
            sharing = FileSharing.rawLoad(data['sharing'], data['id'])
        else:
            sharing = FileSharing(data['id'])
        
        return File(
            accountID=data['accountID'],
            name=data['name'],
            blocked=data['blocked'] == "True",
            sharing=sharing,
            id=data['id'],
            uploadedTimestamp=data['uploadedTimestamp'],
            lastUpdate=data['lastUpdate']
        )
    
    @staticmethod
    def load(id=None, accountID=None, filename=None) -> 'File | List[File] | None':
        if id != None:
            fileData = DI.load(File.ref(id))
            if isinstance(fileData, DIError):
                raise Exception("FILE LOAD ERROR: DIError: {}".format(fileData))
            if fileData == None:
                return None
            if not isinstance(fileData, dict):
                raise Exception("FILE LOAD ERROR: Unexpected DI file load response format; response: {}".format(fileData))
            
            return File.rawLoad(fileData)
        else:
            if accountID == None and filename != None:
                raise Exception("FILE LOAD ERROR: Unexpected load condition.") ## This is because multiple users can have the same file name. Thus, providing just the filename is not enough.
            
            data = DI.load(Ref("files"))
            if isinstance(data, DIError):
                raise Exception("FILE LOAD ERROR: DIError: {}".format(data))
            if data == None:
                return None
            if not isinstance(data, dict):
                raise Exception("FILE LOAD ERROR: Unexpected DI files load response format; response: {}".format(data))

            files: Dict[str, File] = {}
            for fileID in data:
                if isinstance(data[fileID], dict):
                    files[fileID] = File.rawLoad(data[fileID])
            
            # If no accountID, filename is provided, return all files
            if accountID == None and filename == None:
                return list(files.values())
            
            # Look for files that belong to the specified account
            # Loop through all files and return the files that belong to the specified account
            accountFiles = []
            for fileID in files:
                if files[fileID].accountID == accountID:
                    if filename != None and files[fileID].name == filename:
                        return files[fileID]
                    elif filename == None:
                        accountFiles.append(files[fileID])
            
            # If the filename is provided, but no file is found, return None
            if filename != None:
                return None
            
            # If no filename is provided, return the list of account files
            return accountFiles
    
    def save(self, checkIntegrity=True) -> bool:
        convertedData = self.represent()
        
        if checkIntegrity:
            targetAccount = DI.load(Identity.ref(self.accountID))
            if isinstance(targetAccount, DIError):
                raise Exception("FILE SAVE ERROR: DIError: {}".format(targetAccount))
            if targetAccount == None:
                raise Exception("FILE SAVE ERROR: Account not found.")
            if not isinstance(targetAccount, dict):
                raise Exception("FILE SAVE ERROR: Unexpected DI account load response format; response: {}".format(targetAccount))
        
        return DI.save(convertedData, self.originRef)
    
    def linkTo(self, user: Identity):
        user.files[self.id] = self
        return True
    
    def represent(self) -> Dict[str, Any]:
        return {
            "accountID": self.accountID,
            "name": self.name,
            "blocked": str(self.blocked),
            "sharing": self.sharing.represent(),
            "id": self.id,
            "uploadedTimestamp": self.uploadedTimestamp,
            "lastUpdate": self.lastUpdate
        }
    
    def extension(self):
        return File.getExtFrom(self.name)
    
    @staticmethod
    def ref(fileID) -> Ref:
        return Ref("files", fileID)

class FileSharing(DIRepresentable):
    def __init__(self, fileID: str, linkCode: str=None, password: str=None, accessors: int=None, startTimestamp: str=None, active: bool=False) -> None:
        self.linkCode = linkCode
        self.password = password
        self.accessors = accessors
        self.startTimestamp =  startTimestamp
        self.active = active
        self.originRef = FileSharing.ref(fileID)
        
    @staticmethod
    def rawLoad(data: Dict[str, Any], fileID: str) -> 'FileSharing':
        requiredParams = ['linkCode', 'password', 'accessors', 'startTimestamp', 'active']
        for reqParam in requiredParams:
            if reqParam not in data:
                if reqParam in ['active']:
                    data[reqParam] = False
                else:
                    data[reqParam] = None
        
        if isinstance(data['accessors'], str):
            try:
                intValue = int(data['accessors'])
                data['accessors'] = intValue
            except:
                data['accessors'] = None
        
        return FileSharing(
            fileID=fileID,
            linkCode=data['linkCode'],
            password=data['password'],
            accessors=data['accessors'],
            startTimestamp=data['startTimestamp'],
            active=data['active'] == "True"
        )
    
    @staticmethod
    def load(fileID: str) -> 'FileSharing | None':
        data = DI.load(FileSharing.ref(fileID))
        if data == None:
            return None
        if isinstance(data, DIError):
            raise Exception("FILESHARING LOAD ERROR: DIError occurred: {}".format(data))
        if not isinstance(data, dict):
            raise Exception("FILESHARING LOAD ERROR: Unexpected DI load response format; response: {}".format(data))
        
        return FileSharing.rawLoad(data, fileID)
    
    def represent(self) -> Dict[str, Any]:
        return {
            "linkCode": self.linkCode,
            "password": self.password,
            "accessors": self.accessors,
            "startTimestamp": self.startTimestamp,
            "active": str(self.active)
        }
    
    def save(self) -> bool:
        convertedData = self.represent()
        
        return DI.save(convertedData, self.originRef)
    
    def destroy(self):
        return DI.save({}, self.originRef)
    
    @staticmethod
    def ref(fileID: str) -> Ref:
        return Ref("files", fileID, "sharing")