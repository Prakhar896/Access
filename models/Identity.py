from uuid import uuid4
from typing import List, Dict, Any
from . import DIRepresentable, DI, DIError, Ref, AuditLog

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