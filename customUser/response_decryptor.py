from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode


class AESDecryptor:

    def __init__(self, key, iv):
        self.key = key
        self.iv = iv
        self.backend = default_backend()
    
    def decrypt(self, data):
        """
        Decrypt data using AES (CBC mode) and return the plaintext.
        """
        data = b64decode(data)
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(self.iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the data and strip padding
        plaintext = decryptor.update(data) + decryptor.finalize()
        return self._unpad(plaintext).decode('utf-8')

    def _unpad(self, padded_data):
        # Last byte value is the number of padding bytes
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
