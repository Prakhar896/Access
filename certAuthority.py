## This is a certificate authority that issues and revokes digital access certificates.
from operator import index
import random, base64
import datetime, time, json, os, shutil, subprocess

class CertAuthority:
    registeredCertificates = []
    revokedCertificates = []

    @staticmethod
    def encodeToB64(hash):
        hash_bytes = hash.encode("ascii")
        b64_bytes = base64.b64encode(hash_bytes)
        b64_string = b64_bytes.decode("ascii")
        return b64_string
    
    @staticmethod
    def decodeFromB64(encodedHash):
        b64_bytes = encodedHash.encode("ascii")
        hash_bytes = base64.b64decode(b64_bytes)
        hash_string = hash_bytes.decode("ascii")
        return hash_string

    @staticmethod
    def generateCertHash(user):
        # Add random characters into hash
        choices = ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'g', 'G', 'H', 'h', 'i', 'I', 'l', 'L', 'm', 'M', 'n', 'N', 'o', 'O', 'p', 'P', '2', '3', '4', '5', '6', '7', '8', '9', 'x', 'X', 'y', 'Y', 'z', 'Z']
        certHash = ''
        for i in range(1000):
            certHash += random.choice(choices)

        ## Add binary data to the hash
        binChoices = ['0', '1']
        for i in range(512):
            hashAsList = list(certHash)
            random.shuffle(hashAsList)
            indexToUpdate = random.randint(0, len(hashAsList) - 1)
            while hashAsList[indexToUpdate] == "0" or hashAsList[indexToUpdate] == "1":
                indexToUpdate = random.randint(0, len(hashAsList) - 1)
            hashAsList[indexToUpdate] = random.choice(binChoices)
            certHash = ''.join(hashAsList)
        
        hashAsList = list(certHash)
        indexToUpdate = random.randint(0, len(hashAsList) - 1)
        ## Make sure index character is not binary
        while hashAsList[indexToUpdate] == "0" or hashAsList[indexToUpdate] == "1":
            indexToUpdate = random.randint(0, len(hashAsList) - 1)
        
        hashAsList[indexToUpdate] = '"{}"'.format(user[0])
        certHash = ''.join(hashAsList)
        # At the end: 1000 random characters, 512 random binary characters, and the user's first character, total 1002 characters
        certHash = CertAuthority.encodeToB64(certHash)
        return certHash
        
    @staticmethod
    def checkCertificateSecurity(cert):
        def checkValidity():
            try:
                if (len(CertAuthority.decodeFromB64(cert["certificate"])) != 1002) or ('"{}"'.format(cert["user"][0]) not in CertAuthority.decodeFromB64(cert["certificate"])) or (len([i for i in list(CertAuthority.decodeFromB64(cert["certificate"])) if i == '0' or i == '1']) != 512):
                    return False
                else:
                    return True
            except:
                print("There was an error checking the certificate's security. Defaulting to failed security check return...")
                return False

        # Check is certificate is registered, signed by the CA, and has not been revoked
        if cert['user'] in CertAuthority.registeredCertificates and cert['user'] not in CertAuthority.revokedCertificates:
            if checkValidity():
                return CAError.validCert
            else:
                return CAError.invalidCert
        elif cert['user'] in CertAuthority.revokedCertificates:
            if checkValidity():
                return CAError.revokedCertAndValid
            else:
                return CAError.revokedCertNotValid


    @staticmethod
    def issueCertificate(user):
        # This method issues a certificate to a user.
        # The certificate is added to the list of valid certificates.
        # The certificate is returned to the user.
        # Generate an expiry date string of 30 days from now
        certIDOptions = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        certIDString = ''
        for i in range(20):
            certIDString += random.choice(certIDOptions)
        expiryDate = datetime.datetime.now() + datetime.timedelta(days=30)
        expiryDateString = expiryDate.strftime('%Y-%m-%d %H:%M:%S')
        cert = {
            'certID': certIDString,
            'certificate': CertAuthority.generateCertHash(user),
            'expiryDate': expiryDateString,
            'revoked': False,
            'revocationReason': None,
            'revocationDate': None,
            'issueDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        CertAuthority.registeredCertificates[user] = cert
        return cert
    
    @staticmethod
    def revokeCertificate(user, certificateID, reason):
        # This method revokes a certificate.
        # The certificate is added to the list of revoked certificates.
        # The certificate is removed from the list of valid certificates.
        # The certificate is returned to the user.
        for username in CertAuthority.registeredCertificates:
            if CertAuthority.registeredCertificates[username]['certID'] == certificateID and username == user:
                CertAuthority.registeredCertificates[username]['revoked'] = True
                CertAuthority.registeredCertificates[username]['revocationReason'] = reason
                CertAuthority.registeredCertificates[username]['revocationDate'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                CertAuthority.revokedCertificates[user] = CertAuthority.registeredCertificates[username]
                CertAuthority.registeredCertificates.pop(user)
                return CertAuthority.revokedCertificates[user]
        return None

    @staticmethod
    def getCertificate(certID):
        # This method returns a certificate based on the certificate ID.
        for user in CertAuthority.registeredCertificates:
            if CertAuthority.registeredCertificates[user]['certID'] == certID:
                withUserField = CertAuthority.registeredCertificates[user]
                withUserField['user'] = user
                return withUserField
        
        for user in CertAuthority.revokedCertificates:
            if CertAuthority.revokedCertificates[user]['certID'] == certID:
                withUserField = CertAuthority.revokedCertificates[user]
                withUserField['user'] = user
                return withUserField

        return None

    @staticmethod
    def expireOldCertificates():
        expiredCounter = 0
        for username in CertAuthority.registeredCertificates.copy():
            if datetime.datetime.strptime(CertAuthority.registeredCertificates[username]['expiryDate'], '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
                CertAuthority.revokeCertificate(username, CertAuthority.registeredCertificates[username]['certID'], 'This certificate is expired.')
                expiredCounter += 1

        print("CA: Expired {} certificates.".format(expiredCounter))

    @staticmethod
    def renewCertificate(certID):
        certificate = CertAuthority.getCertificate(certID)
        if certificate == None:
            return CAError.noSuchCertFound
        
        if certificate['revoked'] != True:
            return CAError.certIsNotRevoked
        if certificate['user'] not in CertAuthority.revokedCertificates:
            print(CAError.certHasRevokedDetailButNotInRevokedCertificates)
            CertAuthority.revokeCertificate(certificate['user'], certificate['certID'], certificate['revocationReason'])

        # Renew certificate process
        user = certificate.pop('user')

        for username in CertAuthority.revokedCertificates.copy():
            if username == user and CertAuthority.revokedCertificates[user]['certID'] == certificate['certID']:
                CertAuthority.revokedCertificates.pop(user)

        ## Update certificate details
        expiryDate = datetime.datetime.now() + datetime.timedelta(days=30)
        expiryDateString = expiryDate.strftime('%Y-%m-%d %H:%M:%S')
        certificate['expiryDate'] = expiryDateString

        certificate['revoked'] = False
        certificate['revocationReason'] = None
        certificate['revocationDate'] = None
        certificate['renewalDate'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        ## put certificate in registered certificates
        CertAuthority.registeredCertificates[user] = certificate

        return "Successfully renewed certificate with ID: " + certificate['certID']


    @staticmethod
    def loadCertificatesFromFile(fileObject):
        try:
            allCerts = json.load(fileObject)
            regCerts = allCerts['registeredCertificates']
            revokedCerts = allCerts['revokedCertificates']
            CertAuthority.registeredCertificates = regCerts
            CertAuthority.revokedCertificates = revokedCerts
            return "Successfully loaded certificates!"
        except:
            return CAError.loadingCertsFailed

    @staticmethod
    def saveCertificatesToFile(fileObject):
        try:
            allCerts = {
                'registeredCertificates': CertAuthority.registeredCertificates,
                'revokedCertificates': CertAuthority.revokedCertificates
            }
            json.dump(allCerts, fileObject)
            return "Successfully saved certificates!"
        except:
            return CAError.savingCertsFailed

class CAError(Exception):
    def __init__(self, message):
        self.message = message
    
    revokedCertAndValid = "This certificate is revoked and is not active."
    revokedCertNotValid = "This certificate is revoked, not active and it is also not valid as it is not signed by this Certificate Authority."
    invalidCert = "This certificate is not valid as it is not signed and made by this Certificate Authority."
    expiredCertAndValid = "This certificate has expired but it is signed by this Certificate Authority."
    notFoundAndInvalid = "This certificate was not found and was not signed by this Certificate Authority."
    validCertNotValid = "This certificate is registered but it is not signed by this Certificate Authority."
    loadingCertsFailed = "There was an error in loading the certificates from the file provided."
    savingCertsFailed = "There was an error in saving certificate data to the file provided."
    noSuchCertFound = "No such certificate was found associated with that Certificate ID."
    certIsNotRevoked = "The certificate is not revoked. Only revoked certificates can be renewed."
    certHasRevokedDetailButNotInRevokedCertificates = "CAError: The certificate is revoked according to its details but is not in the registered certificates database. Attempting to revoke it before renewing..."


    ## Success Message
    validCert = "This certificate is valid and is signed by this Certificate Authority."

    @staticmethod
    def checkIfErrorMessage(msg):
        arrayOfMsgs = [
            CAError.revokedCertNotValid,
            CAError.revokedCertAndValid,
            CAError.invalidCert,
            CAError.expiredCertAndValid,
            CAError.notFoundAndInvalid,
            CAError.validCertNotValid,
            CAError.loadingCertsFailed,
            CAError.savingCertsFailed,
            CAError.noSuchCertFound,
            CAError.certIsNotRevoked,
            CAError.certHasRevokedDetailButNotInRevokedCertificates
        ]
        if msg in arrayOfMsgs:
            return True
        else:
            return False
