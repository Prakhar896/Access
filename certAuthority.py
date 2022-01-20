## This is a certificate authority that issues and revokes digital access certificates.
import random, base64
from datetime import datetime

class CertAuthority:
    validCertificates = []
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
    def generateCertHash():
        choices = ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'g', 'G', 'H', 'h', 'i', 'I', 'l', 'L', 'm', 'M', 'n', 'N', 'o', 'O', 'p', 'P', '2', '3', '4', '5', '6', '7', '8', '9', 'x', 'X', 'y', 'Y', 'z', 'Z']
        certHash = ''
        for i in range(1000):
            certHash += random.choice(choices)
        binChoices = ['0', '1']
        for i in range(512):
            hashAsList = list(certHash)
            random.shuffle(hashAsList)
            indexToUpdate = random.randint(0, len(hashAsList) - 1)
            hashAsList[indexToUpdate] = random.choice(binChoices)
            certHash = ''.join(hashAsList)

        certHash = CertAuthority.encodeToB64(certHash)
        return certHash
        
    
    @staticmethod
    def issueCertificate(user):
        # This method issues a certificate to a user.
        # The certificate is added to the list of valid certificates.
        # The certificate is returned to the user.

        # Generate an expiry date string of 30 days from now
        expiryDate = datetime.now() + datetime.timedelta(days=30)
        expiryDateString = expiryDate.strftime('%Y-%m-%d %H:%M:%S')
        cert = {
            'user': user,
            'certificate': CertAuthority.generateCertHash(),
            'expiryDate': expiryDateString,
            'revoked': False,
            'revocationReason': None,
            'revocationDate': None,
            'issueDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        CertAuthority.validCertificates.append(cert)
        return cert

