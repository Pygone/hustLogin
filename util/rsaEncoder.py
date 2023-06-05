import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher


class rsaEncoder:
    def __init__(self, userId, password, publicKey):
        self.publicKey = RSA.importKey("-----BEGIN PUBLIC KEY-----\n" + publicKey + "\n-----END PUBLIC KEY-----")
        self.password = password
        self.userId = userId

    def encode(self):
        cipher = PKCS1_cipher.new(self.publicKey, randfunc=None)
        user = base64.b64encode(cipher.encrypt(bytes(self.userId.encode("utf8")))).decode('utf-8')
        passWord = base64.b64encode(cipher.encrypt(bytes(self.password.encode("utf8")))).decode('utf-8')
        return user, passWord
