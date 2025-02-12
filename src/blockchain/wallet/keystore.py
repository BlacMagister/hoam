import os
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from base58 import b58encode_check

class WalletKeystore:
    def __init__(self, path: str = "./wallet.json"):
        self.path = path
        self.keys = self._load_keys()
    
    def _load_keys(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path) as f:
                return json.load(f)
        return {}
    
    def _save_keys(self):
        with open(self.path, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def generate_keypair(self, passphrase: str) -> str:
        private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        public_key = private_key.public_key()
        
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode())
        )
        
        address = b58encode_check(public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint
        )).decode()
        
        self.keys[address] = pem_private.decode()
        self._save_keys()
        return address
    
    def sign_transaction(self, address: str, passphrase: str, data: dict) -> bytes:
        private_pem = self.keys.get(address, "").encode()
        private_key = serialization.load_pem_private_key(
            private_pem,
            password=passphrase.encode(),
            backend=default_backend()
        )
        return private_key.sign(
            json.dumps(data, sort_keys=True).encode(),
            ec.ECDSA(hashes.SHA3_256())
        )
