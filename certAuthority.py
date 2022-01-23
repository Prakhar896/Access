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
            if (len(CertAuthority.decodeFromB64(cert["certificate"])) != 1002) or ('"{}"'.format(cert["user"][0]) not in CertAuthority.decodeFromB64(cert["certificate"])) or (len([i for i in list(CertAuthority.decodeFromB64(cert["certificate"])) if i == '0' or i == '1']) != 512):
                return False
            else:
                return True

        # Check is certificate is registered, signed by the CA, and has not been revoked
        if cert in CertAuthority.registeredCertificates and cert not in CertAuthority.revokedCertificates:
            if checkValidity():
                return CAError.validCert
            else:
                return CAError.invalidCert
        elif cert in CertAuthority.revokedCertificates:
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
            'user': user,
            'certID': certIDString,
            'certificate': CertAuthority.generateCertHash(user),
            'expiryDate': expiryDateString,
            'revoked': False,
            'revocationReason': None,
            'revocationDate': None,
            'issueDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        CertAuthority.registeredCertificates.append(cert)
        return cert
    
    @staticmethod
    def revokeCertificate(user, certHash, reason):
        # This method revokes a certificate.
        # The certificate is added to the list of revoked certificates.
        # The certificate is removed from the list of valid certificates.
        # The certificate is returned to the user.
        for cert in CertAuthority.registeredCertificates:
            if cert['certificate'] == certHash and cert['user'] == user:
                cert['revoked'] = True
                cert['revocationReason'] = reason
                cert['revocationDate'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                CertAuthority.revokedCertificates.append(cert)
                CertAuthority.registeredCertificates.remove(cert)
                return cert
        return None

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


    ## SuccessMessage
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
            CAError.loadingCertsFailed
        ]
        if msg in arrayOfMsgs:
            return True
        else:
            return False