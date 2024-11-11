from uuid import uuid4
from typing import List, Dict, Any
from database import *
from database import DIRepresentable
from services import Universal

class Identity(DIRepresentable):
    def __init__(self, username: str, email: str, password: str, lastLogin: str, authToken: str, auditLogs: 'Dict[str, AuditLog]', otpCode: str, created: str, files: 'Dict[str, File]', id: str=None) -> None:
        if id == None:
            id = uuid4().hex
        
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.lastLogin = lastLogin
        self.authToken = authToken
        self.auditLogs = auditLogs
        self.otpCode = otpCode
        self.created = created
        self.files = files
        self.originRef = Identity.ref(id)
        
    @staticmethod
    def rawLoad(data: dict) -> 'Identity':
        requiredParams = ['username', 'email', 'password', 'lastLogin', 'authToken', 'auditLogs', 'otpCode', 'created', 'files', 'id']
        for reqParam in requiredParams:
            if reqParam not in data:
                if reqParam in ['auditLogs', 'files']:
                    data[reqParam] = {}
                else:
                    data[reqParam] = None
        
        logs = {}
        for logID in data['auditLogs']:
            if data['auditLogs'][logID] == None:
                continue
            logs[logID] = AuditLog.rawLoad(data['auditLogs'][logID])
            
        files = {}
        for fileID in data['files']:
            if data['files'][fileID] == None:
                continue
            files[fileID] = File.rawLoad(data['files'][fileID])
        
        return Identity(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            lastLogin=data['lastLogin'],
            authToken=data['authToken'],
            auditLogs=logs,
            otpCode=data['otpCode'],
            created=data['created'],
            files=files,
            id=data['id']
        )
    
    @staticmethod
    def load(id=None, username=None, email=None, authToken=None) -> 'Identity | List[Identity] | None':
        if id == None:
            data = DI.load(Ref("accounts"))
            if data == None:
                return None
            if not isinstance(data, dict):
                raise Exception("IDENTITY LOAD ERROR: Failed to load dictionary accounts data; response: {}".format(data))

            identities: Dict[str, Identity] = {}
            for id in data:
                identities[id] = Identity.rawLoad(data[id])
            
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
            
            return Identity.rawLoad(data)
        
    def represent(self) -> Dict[str, Any]:
        auditLogs = {logID: self.auditLogs[logID].represent() for logID in self.auditLogs}
        files = {fileID: self.files[fileID].represent() for fileID in self.files}
        
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "lastLogin": self.lastLogin,
            "authToken": self.authToken,
            "auditLogs": auditLogs,
            "otpCode": self.otpCode,
            "created": self.created,
            "files": files
        }
        
    def save(self):
        convertedData = self.represent()
        
        return DI.save(convertedData, self.originRef)
    
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
    
class AuditLog(DIRepresentable):
    def __init__(self, accountID: str, event: str, text: str, id: str=None, timestamp: str=Universal.utcNowString()) -> None:
        if id == None:
            id = uuid4().hex
            
        self.id = id
        self.accountID = accountID
        self.timestamp = timestamp
        self.event = event
        self.text = text
        self.originRef = AuditLog.ref(accountID, id)
        
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
        accountsData = DI.load(Ref("accounts"))
        if accountsData == None:
            return None
        if not isinstance(accountsData, dict):
            raise Exception("AUDITLOG LOAD ERROR: Failed to load dictionary accounts data; response: {}".format(accountsData))
        
        if id == None and accountID == None:
            # Load all logs
            auditLogs: List[AuditLog] = []
            for accountID in accountsData:
                accountData = accountsData[accountID]
                if "auditLogs" in accountData:
                    for logID in accountData["auditLogs"]:
                        auditLogs.append(AuditLog.rawLoad(accountData["auditLogs"][logID]))
            
            return auditLogs
        elif id == None and accountID != None:
            # Load all logs for the targeted account
            if accountID not in accountsData:
                return None
            
            accountData = accountsData[accountID]
            if "auditLogs" not in accountData:
                return None
            if not isinstance(accountData["auditLogs"], dict):
                raise Exception("AUDITLOG LOAD ERROR: Corrupted auditLogs data for account '{}'; data: {}".format(accountID, accountData["auditLogs"]))
            
            auditLogs: List[AuditLog] = []
            for logID in accountData["auditLogs"]:
                auditLogs.append(AuditLog.rawLoad(accountData["auditLogs"][logID]))
            
            return auditLogs
        elif id != None and accountID == None:
            # Search all accounts for the targeted log
            for accountID in accountsData:
                accountData = accountsData[accountID]
                if "auditLogs" in accountData:
                    if not isinstance(accountData["auditLogs"], dict):
                        continue
                    for logID in accountData["auditLogs"]:
                        if logID == id:
                            return AuditLog.rawLoad(accountData["auditLogs"][logID])
            
            return None
        else:
            # Search the targeted account for the targeted log
            if accountID not in accountsData:
                return None
            
            accountData = accountsData[accountID]
            if "auditLogs" not in accountData:
                return None
            if not isinstance(accountData["auditLogs"], dict):
                raise Exception("AUDITLOG LOAD ERROR: Corrupted auditLogs data for account '{}'; data: {}".format(accountID, accountData["auditLogs"]))
            
            for logID in accountData["auditLogs"]:
                if logID == id:
                    return AuditLog.rawLoad(accountData["auditLogs"][logID])
            
            return None

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
    
    @staticmethod
    def ref(accountID, logID) -> Ref:
        return Ref("accounts", accountID, "auditLogs", logID)
    
class File(DIRepresentable):
    def __init__(self, accountID: str, name: str, blocked: bool=False, id: str=None, uploadedTimestamp: str=None) -> None:
        if id == None:
            id = uuid4().hex
        if uploadedTimestamp == None:
            uploadedTimestamp = Universal.utcNowString()
            
        self.id = id
        self.accountID = accountID
        self.name = name
        self.uploadedTimestamp = uploadedTimestamp
        self.blocked = blocked
        self.originRef = File.ref(accountID, id)
        
    @staticmethod
    def getExtFrom(fileName: str):
        return fileName.split(".")[-1]
        
    @staticmethod
    def rawLoad(data: Dict[str, Any]) -> 'File':
        requiredParams = ['accountID', 'name', 'blocked', 'id', 'uploadedTimestamp']
        for reqParam in requiredParams:
            if reqParam not in data:
                data[reqParam] = None
        
        return File(
            accountID=data['accountID'],
            name=data['name'],
            blocked=data['blocked'] == "True",
            id=data['id'],
            uploadedTimestamp=data['uploadedTimestamp']
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
    
    def represent(self) -> Dict[str, Any]:
        return {
            "accountID": self.accountID,
            "name": self.name,
            "blocked": str(self.blocked),
            "id": self.id,
            "uploadedTimestamp": self.uploadedTimestamp
        }
    
    def extension(self):
        return File.getExtFrom(self.name)
    
    @staticmethod
    def ref(accountID, fileID) -> Ref:
        return Ref("accounts", accountID, "files", fileID)