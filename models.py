from uuid import uuid4
from typing import List, Dict, Any
from database import *
from services import Universal
from utils import Ref

class Identity(DIRepresentable):
    def __init__(self, username: str, email: str, password: str, lastLogin: str, authToken: str, auditLogs: 'Dict[str, AuditLog]'={}, emailVerification: 'EmailVerification'=None, created: str=None, files: 'Dict[str, File]'={}, id: str=None) -> None:
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
        self.auditLogs = auditLogs
        self.emailVerification = emailVerification
        self.created = created
        self.files = files
        self.originRef = Identity.ref(id)
        
        self.auditLogsLoaded = False
        
    @staticmethod
    def rawLoad(data: dict, loadAuditLogs=False) -> 'Identity':
        requiredParams = ['username', 'email', 'password', 'lastLogin', 'authToken', 'emailVerification', 'created', 'files', 'id']
        for reqParam in requiredParams:
            if reqParam not in data:
                if reqParam in ['files', 'emailVerification']:
                    data[reqParam] = {}
                else:
                    data[reqParam] = None
        
        files = {}
        for fileID in data['files']:
            if data['files'][fileID] == None:
                continue
            files[fileID] = File.rawLoad(data['files'][fileID])
        
        emailVerification = EmailVerification.rawLoad(data['emailVerification'], data['id'])
        
        account = Identity(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            lastLogin=data['lastLogin'],
            authToken=data['authToken'],
            emailVerification=emailVerification,
            created=data['created'],
            files=files,
            id=data['id']
        )
        
        if loadAuditLogs:
            account.getAuditLogs()
        
        return account
    
    @staticmethod
    def load(id=None, username=None, email=None, authToken=None, withAuditLogs=False) -> 'Identity | List[Identity] | None':
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
                identities[id] = Identity.rawLoad(data[id], loadAuditLogs=withAuditLogs)
            
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
            
            return Identity.rawLoad(data, loadAuditLogs=withAuditLogs)
        
    def represent(self) -> Dict[str, Any]:
        files = {fileID: self.files[fileID].represent() for fileID in self.files}
        
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "lastLogin": self.lastLogin,
            "authToken": self.authToken,
            "emailVerification": self.emailVerification.represent(),
            "created": self.created,
            "files": files
        }
        
    def save(self):
        convertedData = self.represent()
        
        return DI.save(convertedData, self.originRef)
    
    def getAuditLogs(self):
        accountLogs = AuditLog.load(accountID=self.id)
        if accountLogs == None:
            self.auditLogs = {}
            return True
        if not isinstance(accountLogs, list):
            raise Exception("IDENTITY GETAUDITLOGS ERROR: Unexpected response format; response: {}".format(accountLogs))

        self.auditLogs = {log.id: log for log in accountLogs}
        self.auditLogsLoaded = True
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
        
        print("AL: {}: {}: {}".format(id, event, text))
            
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
            
            return [AuditLog.rawLoad(logData) for logData in logs.values()]

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
    def __init__(self, accountID: str, name: str, blocked: bool=False, id: str=None, uploadedTimestamp: str=None, lastUpdate: str=None) -> None:
        if id == None:
            id = uuid4().hex
        if uploadedTimestamp == None:
            uploadedTimestamp = Universal.utcNowString()
            
        self.id = id
        self.accountID = accountID
        self.name = name
        self.blocked = blocked
        self.uploadedTimestamp = uploadedTimestamp
        self.lastUpdate = lastUpdate
        self.originRef = File.ref(accountID, id)
        
    @staticmethod
    def getExtFrom(fileName: str):
        return fileName.split(".")[-1]
        
    @staticmethod
    def rawLoad(data: Dict[str, Any]) -> 'File':
        requiredParams = ['accountID', 'name', 'blocked', 'id', 'uploadedTimestamp', 'lastUpdate']
        for reqParam in requiredParams:
            if reqParam not in data:
                data[reqParam] = None
        
        return File(
            accountID=data['accountID'],
            name=data['name'],
            blocked=data['blocked'] == "True",
            id=data['id'],
            uploadedTimestamp=data['uploadedTimestamp'],
            lastUpdate=data['lastUpdate']
        )
    
    @staticmethod
    def load(id=None, accountID=None) -> 'File | List[File] | None':
        accountsData = DI.load(Ref("accounts"))
        if accountsData == None:
            return None
        if not isinstance(accountsData, dict):
            raise Exception("FILE LOAD ERROR: Failed to load dictionary accounts data; response: {}".format(accountsData))
        
        if id == None and accountID == None:
            # Load all files
            files: List[File] = []
            for accountID in accountsData:
                accountData = accountsData[accountID]
                if "files" in accountData:
                    for fileID in accountData["files"]:
                        files.append(File.rawLoad(accountData["files"][fileID]))
            
            return files
        elif id == None and accountID != None:
            # Load all files for the targeted account
            if accountID not in accountsData:
                return None
            
            accountData = accountsData[accountID]
            if "files" not in accountData:
                return None
            if not isinstance(accountData["files"], dict):
                raise Exception("FILE LOAD ERROR: Corrupted files data for account '{}'; data: {}".format(accountID, accountData["files"]))
            
            files: List[File] = []
            for fileID in accountData["files"]:
                files.append(File.rawLoad(accountData["files"][fileID]))
            
            return files
        elif id != None and accountID == None:
            # Search all accounts for the targeted file
            for accountID in accountsData:
                accountData = accountsData[accountID]
                if "files" in accountData:
                    if not isinstance(accountData["files"], dict):
                        continue
                    for fileID in accountData["files"]:
                        if fileID == id:
                            return File.rawLoad(accountData["files"][fileID])
            
            return None
        else:
            # Search the targeted account for the targeted file
            if accountID not in accountsData:
                return None
            
            accountData = accountsData[accountID]
            if "files" not in accountData:
                return None
            if not isinstance(accountData["files"], dict):
                raise Exception("FILE LOAD ERROR: Corrupted files data for account '{}'; data: {}".format(accountID, accountData["files"]))
            
            for fileID in accountData["files"]:
                if fileID == id:
                    return File.rawLoad(accountData["files"][fileID])
            
            return None
    
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
            "id": self.id,
            "uploadedTimestamp": self.uploadedTimestamp,
            "lastUpdate": self.lastUpdate
        }
    
    def extension(self):
        return File.getExtFrom(self.name)
    
    @staticmethod
    def ref(accountID, fileID) -> Ref:
        return Ref("accounts", accountID, "files", fileID)