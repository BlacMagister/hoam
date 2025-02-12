import os
import json
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from hashlib import scrypt

class SecureKeystore:
    def __init__(self, path: str = "wallet.keystore"):
        self.path = path
        self._master_key = None
        self.keys = {}

    def initialize(self, password: str):
        salt = os.urandom(16)
        key = scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
        self._master_key = Fernet(b64encode(key))
        self._save_keystore(salt)

    def _save_keystore(self, salt: bytes):
        data = {
            "salt": b64encode(salt).decode(),
            "keys": {k: self._master_key.encrypt(v).decode() 
                    for k, v in self.keys.items()}
        }
        with open(self.path, 'w') as f:
            json.dump(data, f)

    def generate_keypair(self):
        private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint
        )
        self.keys[public_key.hex()] = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        self._save_keystore()
        return public_key.hex()
