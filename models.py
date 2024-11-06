from uuid import uuid4
from typing import List, Dict, Any
from database import *
from services import Universal

class Identity(DIRepresentable):
    def __init__(self, username: str, email: str, password: str, lastLogin: str, authToken: str, auditLogs: str, created: str, files, id=uuid4().hex) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.lastLogin = lastLogin
        self.authToken = authToken
        self.auditLogs = auditLogs
        self.created = created
        self.files = files
        self.originRef = Identity.ref(id)
        
    @staticmethod
    def rawLoad(data: dict) -> 'Identity':
        requiredParams = ['username', 'email', 'password', 'lastLogin', 'authToken', 'auditLogs', 'created', 'files', 'id']
        for reqParam in requiredParams:
            if reqParam not in data:
                data[reqParam] = None
        
        return Identity(
            data['username'],
            data['email'],
            data['password'],
            data['lastLogin'],
            data['authToken'],
            data['auditLogs'],
            data['created'],
            data['files'],
            data['id']
        )
    
    @staticmethod
    def load(id=None, username=None, email=None) -> 'Identity | List[Identity] | None':
        if id == None:
            data = DI.load(Ref("accounts"))
            if data == None:
                return None
            if not isinstance(data, dict):
                raise Exception("IDENTITY LOAD ERROR: Failed to load dictionary accounts data; response: {}".format(data))

            identities: Dict[str, Identity] = {}
            for id in data:
                identities[id] = Identity.rawLoad(data[id])
            
            if username == None and email == None:
                return list(identities.values())
            
            for identityID in identities:
                targetIdentity = identities[identityID]
                if username != None and targetIdentity.username == username:
                    return targetIdentity
                elif email != None and targetIdentity.email == email:
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
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "lastLogin": self.lastLogin,
            "authToken": self.authToken,
            "auditLogs": self.auditLogs,
            "created": self.created,
            "files": self.files
        }
        
    def save(self):
        convertedData = self.represent()
        
        return DI.save(convertedData, self.originRef)
    
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