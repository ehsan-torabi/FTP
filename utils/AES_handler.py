import marshal

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class AES_encryptor(object):
    def __init__(self, key_length: int):
        self.key_length = key_length
        self.key = get_random_bytes(key_length)
        self.iv = get_random_bytes(AES.block_size)
        self.cipher = AES.new(self.key, AES.MODE_CFB,self.iv)


    def get_key(self) -> bytes:
        return self.key
    def get_iv(self) -> bytes:
        return self.iv
    def save_key(self):
        information = {"key_length": self.key_length, "key": self.key, "iv": self.iv}
        with open(".aes_key", "wb") as key_file:
            key_file.write(marshal.dumps(information))

    def encrypt_data(self, data: str | bytes) -> (bytes, bytes):
        if isinstance(data, str):
            ciphertext = self.cipher.encrypt(data.encode())
            old_iv = self.cipher.iv
            self.cipher = AES.new(self.key, AES.MODE_CFB,self.iv)
            return ciphertext, old_iv
        elif isinstance(data, bytes):
            ciphertext = self.cipher.encrypt(data)
            old_iv = self.cipher.iv
            self.cipher = AES.new(self.key, AES.MODE_CFB,self.iv)
            return ciphertext, old_iv


class AES_decryptor(object):
    def __init__(self, key: bytes,iv: bytes):
        self.key = key
        self.iv = iv

    @staticmethod
    def read_key(key_file_path: str):
        with open(key_file_path, "rb") as key_file:
            information = marshal.loads(key_file.read())
            return AES_decryptor(information["key"], information["iv"])

    def get_key(self) -> bytes:
        return self.key

    def decrypt_data(self, ciphertext) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CFB,self.iv)
        decrypted = cipher.decrypt(ciphertext)
        return decrypted
