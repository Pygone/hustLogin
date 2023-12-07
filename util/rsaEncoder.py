import base64

from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto.PublicKey import RSA


class RsaEncoder:
    def __init__(self, user_id, password, public_key):
        self.public_key = RSA.importKey(f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----")
        self.password = password
        self.user_id = user_id

    def encode(self):
        cipher = PKCS1_cipher.new(self.public_key)
        encoded_user_id = base64.b64encode(cipher.encrypt(self.user_id.encode())).decode()
        encoded_password = base64.b64encode(cipher.encrypt(self.password.encode())).decode()
        return encoded_user_id, encoded_password
