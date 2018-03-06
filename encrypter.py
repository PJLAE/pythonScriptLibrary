#! /usr/bin/python36
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
#[]  Script: encrypter.py                                                      []
#[]  Script Language: Python 3.6(.4)                                           []
#[]  Description: Uses Fernet Cryptography to offer a basic set of encryption, []
#[]               decryption, and key generation methods that can be used      []
#[]               to encrypt/decrypt passwords using a secure key file along   []
#[]               with a key generation method.                                []
#[]  Author: Paul J. Laue                                                      []
#[]  Created: February 23, 2018 11:17:00 AM                                    []
#[] ========================================================================== []
#[]  CHANGE LOG                                                                []
#[]  ----------                                                                []
#[]                                                                            []
#[] ========================================================================== []
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
from cryptography.fernet import Fernet
import base64
import os.path
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from enum import Enum

class PublicKeyFormatType(Enum):
    """
    An enumeration describing the type of public key
    """
    OpenSSH = 0,
    PEM = 1

class DigestSize(Enum):
    """
    A enumeration of valid digest sizes
    """
    sz32 = 32,
    sz64 = 64

class RSAKeySize(Enum):
    """
    An enumeration of RSA key sizes.
    """
    sz1024 = 1024,
    sz2048 = 2048,
    sz4096 = 4096

class Encrypter:
    """
    This class handles an implementation for a set of basic encryption/decryption, and
    key generation techniques that can be used to encrypt/decrypt passwords using a securely
    generated key file.  This class also provides a way to generate the secure key if needed.
    """
    def __init__(self, keyFile=None):
        """
        Creates a new empty Encrypter object.
        
        @param keyFile (optional): location of the secure key to use for encryption/decryption
        @type keyFile: String
               
        @raise OSError when key file does not exist or is invalid.
        """
        self._errMsg = ''
        self._outMsg = ''        
        if not keyFile is None and not self.setSecureKey(keyFile):
            raise OSError("The key file '{keyFile}' does not exist or is invalid!".format(keyFile=keyFile))
        
        self._passPhrase = None
            
    def directoryExists(self, directory):
        """
        Attempts to validate whether a directory exists or not.
        
        @param directory: path to validate if exists or not.
        @type directory: String
        
        @return Boolean
        """
        if directory is None:
            return False
        elif type(directory) == str:            
            return os.path.isdir(directory)
        else:
            return False
    
    def filesExist(self, files):
        """
        Attempts to validate whether files exist or not.
        
        @param files: a list of files to validate
        @type files: List/Sequence
        
        @return Boolean 
        """
        if files is None:
            return False
        elif type(files) == str:
            if not os.path.isfile(files): return False 
        else:
            for fl in files:
                if not os.path.isfile(fl): return False
                
        return True
    
    def getErrorMsg(self):
        """
        Returns any error messages on the stack.
        
        @return String
        """
        return self._errMsg
    
    def getOutputMsg(self):
        """
        Returns any output messages on the stack.
        
        @return String
        """
        return self._outMsg
    
    def getMD5HashedString(self, textToHash):
        """
        Returns a MD5 digest using the text passed to the method.
        
        @param textToHash: input text to output as a hash digest
        @type textToHas: String
        
        @return String
        """
        if len(textToHash) > 0:
            return hashlib.md5(str.encode(textToHash)).hexdigest()
        else:
            return None
        
    def getSHA256HashedString(self, textToHash):
        """
        Returns a SHA256 digest using text passed to the method.
        
        @param textToHash: input text to output as a hash digest
        @type textToHas: String
        
        @return String
        """
        if len(textToHash) > 0:
            return hashlib.sha256(str.encode(textToHash)).hexdigest()
        else:
            return None
        
    def getSHA512HashedString(self, textToHash):
        """
        Returns a SHA512 digest using text passed to the method.
        
        @param textToHash: input text to output as a hash digest
        @type textToHas: String
        
        @return String
        """
        if len(textToHash) > 0:
            return hashlib.sha512(str.encode(textToHash)).hexdigest()
        else:
            return None
        
    def getBlake2HashedString(self, textToHash, digestSize=DigestSize.sz32):
        """
        Returns a Blake2 digest using text passed to the method.
        
        @param textToHash: input text to output as a hash digest
        @type textToHas: String
        
        @param digestSize = specifies the digest size to use for platform dependency.
        @type digestSize: Enumerator
        
        @return String
        """
        if len(textToHash) > 0:
            if digestSize == DigestSize.sz64:
                return hashlib.blake2b(str.encode(textToHash), digest_size=64).hexdigest()
            else:
                return hashlib.blake2s(str.encode(textToHash), digest_size=32).hexdigest()
        else:
            return None

    def setSecureKey(self, keyFile):
        """
        Set the path to key and the secure key itself
        
        @param keyFile: location of the secure key to use for encryption/decryption
        @type keyFile: String
        
        @return Boolean
        """
        if not self.filesExist(keyFile):
            self._outMsg = "Path '{keyFile}' does not exist or is invalid!".format(keyFile=keyFile) 
            return False
        
        try:
            self._securekeyfile = keyFile
            with open(keyFile) as key:
                self._securekey = str.encode(key.read())
            return True
        except OSError as oerr:
            self._errMsg = "There was a critical error attempting to open key file '{0}'.  OSError={1}".format(keyFile, str(oerr))
            return False
        
    def setPassPhrase(self, passPhrase):
        """
        Set the passphrase to use with the encrypted key.
        
        @param passPhrase: a passphrase to use with the encrypted key
        @type passPhrase: String
        """
        if len(passPhrase) > 0:
            self._passPhrase = passPhrase
    
    def encrypt(self, textToEncrypt):
        """
        Uses the secure key to encrypt a string of text.
        
        @param textToEncrypt: a string of text the encrypt
        @type textToEncrypt: String
        
        @return String
        """
        if (len(textToEncrypt) == 0): 
            self._errMsg = "A string to encrypt was not provided."
            return None
        else:
            # is the encryption key set? if not throw error.
            if self._securekey is None:
                raise Exception("The secure key used for encryption has not been set.  Use 'setSecureKey' to set the key file.")
    
            thiskey = base64.urlsafe_b64decode(self._securekey)
            thiscipher = Fernet(thiskey)
            
            texttoencryptasbytes = str.encode(textToEncrypt)
            encodedtextasbytes = thiscipher.encrypt(texttoencryptasbytes)
        
            return encodedtextasbytes.decode('utf-8')
                
    def encryptRSA(self, textToEncrypt, keyFormat):
        """
        Encrypt some text using RSA.
        
        @param textToEncrypt: a string of text the encrypt
        @type textToEncrypt: String
        
        @param keyFormat: format type of key file (OpenSSH, PEM)
        @type Enumerator (PublicKeyFormatType)
              
        @return String
        """
        if (len(textToEncrypt) == 0): 
            self._errMsg = "A string to encrypt was not provided."
            return None
        else:
            if self._securekeyfile is not None:
                with open(self._securekeyfile, 'rb') as key_file:
                    if keyFormat == PublicKeyFormatType.OpenSSH:
                        key = serialization.load_ssh_public_key(key_file.read(), backend=default_backend())
                    elif keyFormat == PublicKeyFormatType.PEM:
                        key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())
                    else:
                        raise ValueError("The key format '{keyFormat}' is not valid!".format(keyFormat=keyFormat))
            
                ciphertext = key.encrypt(textToEncrypt, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
                return ciphertext
#                return ciphertext.decode('utf-8') 
            else:
                self._errMsg = "Key file is missing or invalid!"
                return None
                
    def decryptRSA(self, encryptedText):
        """
        Decrypt some text using RSA
        
        @param encryptedText = string of encrypted text to decrypt
        @type encryptedText = String
        
        @return String
        """
        if (len(encryptedText) == 0): 
            self._errMsg = "A string to decrypt was not provided."
            return None
        else:
            if self._securekeyfile is not None:
                with open(self._securekeyfile, 'rb') as key_file:
                    if self._passPhrase:
                        pwd = str.encode(self._passPhrase)
                        key = serialization.load_pem_private_key(key_file.read(), password=pwd, backend=default_backend())
                    else:
                        key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())
                
                plaintext = key.decrypt(encryptedText, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

                return plaintext
#                return plaintext.decode('utf-8')
            else:
                self._errMsg = "Key file is missing or invalid!"
                return None
        
    def decrypt(self, encryptedText):
        """
        Uses the secure key to decrypt a string of encrypted text.
        
        @param encryptedText = string of encrypted text to decrypt
        @type encryptedText = String
        
        @return String
        """
        if (len(encryptedText) == 0): 
            self._errMsg = "A string to decrypt was not provided."
            return None
        else:
            # is the encryption key set? if not throw error.
            if self._securekey is None:
                raise Exception("The secure key used for encryption has not been set.  Use 'setSecureKey' to set the key file.")

            thiskey = base64.urlsafe_b64decode(self._securekey)        
            thiscipher = Fernet(thiskey)
        
            texttodecryptasbytes = str.encode(encryptedText)
            decodedtextasbytes = thiscipher.decrypt(texttodecryptasbytes)
        
            return decodedtextasbytes.decode('utf-8')
        
    def sign(self, textToSign):
        """
        Sign some text using RSA.
        
        @param textToSign: some text to add signature to
        @type String
        
        @return String
        """
        if (len(textToSign) == 0): 
            self._errMsg = "A string to sign was not provided."
            return None
        else:
            if self._securekeyfile is not None:
                with open(self._securekeyfile, 'rb') as key_file:
                    if self._passPhrase:
                        key = serialization.load_pem_private_key(key_file.read(), password=self._passPhrase, backend=default_backend())
                    else:
                        key = serialization.load_pem_private_key(key_file.read(), backend=default_backend())
                        
                    ciphertext = key.sign(str.encode(textToSign), padding.PSS(mfg=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                    
                    return ciphertext.decode('utf-8')
            else:
                self._errMsg = "Key file is missing or invalid!"
                return None
        
    def generateKey(self):
        """
        Uses Fernet module to generate a key and returns a base64 safe key string
        """    
        return base64.urlsafe_b64encode(Fernet.generate_key())
    
    def getRSAKeySize(self, keySize):
        """
        Validates key size.
        
        @param keySize: size of key
        @type keySize: Integer
        
        @return Integer
        """
        if keySize == RSAKeySize.sz1024:
            return 1024
        elif keySize == RSAKeySize.sz4096:
            return 4096        
        else:
            return 2048        
        
    def generateRSAKeyPair(self, keySize=RSAKeySize.sz2048, publicKeyFormat=PublicKeyFormatType.PEM, passPhrase=None):
        """
        Uses cryptography modules hazardous materials (hazmat) to generate a private and public key pair. 
        
        @param keySize: a reference to the size of key to use during generation.
        @type keySize: Enumerator
        
        @param publicKeyFormatType (optional): format type of public key to generate
        @type publicKeyFormatType: Enumerator
        
        @param passPhrase (optional): a phrase to use when serializing the private key
        @type passPhrase: String
        
        @return Tuple containing public and private key as pem
        """
        keysize = self.getRSAKeySize(keySize)
            
        # generate private/public key pair
        key = rsa.generate_private_key(public_exponent=65537, key_size=keysize, backend=default_backend())
        
        # get public key in OpenSSH format
        if publicKeyFormat == PublicKeyFormatType.OpenSSH:
            encoding = serialization.Encoding.OpenSSH
            pubformat = serialization.PublicFormat.OpenSSH
        else:
            encoding = serialization.Encoding.PEM
            pubformat = serialization.PublicFormat.SubjectPublicKeyInfo
            
        public_key = key.public_key().public_bytes(encoding, pubformat)
        
        # get private key in PEM container format
        if passPhrase:
            encryption = serialization.BestAvailableEncryption(str.encode(passPhrase))
        else:
            encryption = serialization.NoEncryption()            
            
        pem = key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=encryption)
        
        return public_key, pem
        
    def writeRSAKeyPair(self, publicKey, privateKey, keySize=None, publicKeyFormat=PublicKeyFormatType.PEM, passPhrase=None):
        """
        Writes an RSA key pair to disk that is generated by hazardous materials (hazmat) within cryptography module.
        
        @param publicKey: the public key of an RSA key pair.
        @type publicKey: 
        
        @param privateKey: the private key of an RSA key pair.
        @type private Key:
        
        @param keySize (optional) = size of rsa key
        @type keySize = Integer
        
        @param publicKeyFormatType (optional): format type of public key to generate
        @type publicKeyFormatType: Enumerator
        
        @param passPhrase (optional): a phrase to use when serializing the private key
        @type passPhrase: String
        
        @return Boolean
        """
        if passPhrase:
            if publicKeyFormat:
                pubkey, pem = self.generateRSAKeyPair(keySize, publicKeyFormat, passPhrase)
            else:
                pubkey, pem = self.generateRSAKeyPair(keySize, passPhrase)
        else:
            if publicKeyFormat:
                pubkey, pem = self.generateRSAKeyPair(keySize, publicKeyFormat)
            else:
                pubkey, pem = self.generateRSAKeyPair(keySize)
                
        
        pubkeystr = pubkey.decode('utf-8')
                
        try:
            # write public key to File
            with open(publicKey, 'wb') as pf:
                pf.write(pubkey)
            
            # write private key to File
            with open(privateKey, 'wb') as pf:
                pf.write(pem)
        
        except OSError as oerr:
            self._errMsg = "Critical error while generating rsa key pair. OSError={oerr}".format(oerr=oerr)
            return False
            
        self._outMsg = pubkeystr
        
        return True