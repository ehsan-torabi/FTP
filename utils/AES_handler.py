from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import marshal

from Crypto.Util.Padding import pad,unpad


class AES_encryptor(object):
    def __init__(self, key_length: int):
        self.key_length = key_length
        self.key = get_random_bytes(key_length)
        self.cipher = AES.new(self.key, AES.MODE_CBC)

    def get_key(self) -> bytes:
        return self.key

    def save_key(self):
        information = {"key_length": self.key_length, "key": self.key}
        with open(".aes_key", "wb") as key_file:
            key_file.write(marshal.dumps(information))

    def encrypt_data(self, data: str | bytes)->(bytes,bytes):
        if isinstance(data, str):
            ciphertext = self.cipher.encrypt(pad(data.encode(), AES.block_size))
            old_iv = self.cipher.iv
            self.cipher = AES.new(self.key, AES.MODE_CBC)
            return ciphertext,old_iv
        elif isinstance(data, bytes):
            ciphertext = self.cipher.encrypt(pad(data, AES.block_size))
            old_iv = self.cipher.iv
            self.cipher = AES.new(self.key, AES.MODE_CBC)

            return ciphertext,old_iv



class AES_decryptor(object):
    def __init__(self, key:bytes):
        self.key = key

    @staticmethod
    def read_key(key_file_path:str):
        with open(key_file_path, "rb") as key_file:
            information = marshal.loads(key_file.read())
            return AES_decryptor(information["key"])

    def get_key(self)->bytes:
        return self.key

    def decrypt_data(self,ciphertext,iv)-> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC,iv)
        decrypted = cipher.decrypt(ciphertext)
        return unpad(decrypted,AES.block_size)


