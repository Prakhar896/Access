from uuid import uuid4
from typing import List, Dict, Any
from . import DIRepresentable, DI, DIError, Ref, Identity
from services import Universal

class AuditLog(DIRepresentable):
    def __init__(self, accountID: str, event: str, text: str, id: str=uuid4().hex, timestamp: str=Universal.utcNowString()) -> None:
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
            data['event'],
            data['text'],
            data['id'],
            data['accountID'],
            data['timestamp']
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