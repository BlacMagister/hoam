import os
import json
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

class SecureKeystore:
    def __init__(self, path: str = "vault.dat"):
        self.path = path
        self._vault = self._load_vault()
        self._current_key = None
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA3_256(),
            length=32,
            salt=salt,
            iterations=1000000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def _load_vault(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                return json.loads(f.read())
        return {"keys": {}}
    
    def _save_vault(self):
        with open(self.path, "wb") as f:
            f.write(json.dumps(self._vault).encode())
    
    def unlock(self, password: str):
        salt = b64decode(self._vault["salt"])
        key = self._derive_key(password, salt)
        self._current_key = Fernet(b64encode(key))
    
    def generate_keypair(self, password: str, alias: str):
        if not self._current_key:
            raise Exception("Vault locked")
        
        private_key = ec.generate_private_key(ec.SECP256K1())
        public_key = private_key.public_key()
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        encrypted_pem = self._current_key.encrypt(pem)
        self._vault["keys"][alias] = {
            "public": public_key.public_bytes(
                serialization.Encoding.X962,
                serialization.PublicFormat.CompressedPoint
            ).hex(),
            "private": b64encode(encrypted_pem).decode()
        }
        self._save_vault()
    
    def sign_transaction(self, alias: str, data: dict) -> str:
        if alias not in self._vault["keys"]:
            raise Exception("Key alias not found")
        
        encrypted_pem = b64decode(self._vault["keys"][alias]["private"])
        decrypted_pem = self._current_key.decrypt(encrypted_pem)
        private_key = serialization.load_pem_private_key(
            decrypted_pem,
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(
            json.dumps(data, sort_keys=True).encode(),
            ec.ECDSA(hashes.SHA3_256())
        )
        return signature.hex()
