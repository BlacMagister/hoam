from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.exceptions import InvalidSignature
from typing import Tuple
import hashlib

class TransactionSigner:
    def __init__(self, curve=ec.SECP256K1()):
        self.curve = curve

    def generate_keypair(self) -> Tuple[ec.EllipticCurvePrivateKey, bytes]:
        private_key = ec.generate_private_key(self.curve)
        public_key = private_key.public_key().public_bytes(
            encoding=Encoding.X962,
            format=PublicFormat.CompressedPoint
        )
        return private_key, public_key

    def sign_message(self, private_key: ec.EllipticCurvePrivateKey, message: bytes) -> bytes:
        return private_key.sign(
            message,
            ec.ECDSA(hashes.SHA3_256())
        
    def verify_signature(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        try:
            pub_key = ec.EllipticCurvePublicKey.from_encoded_point(self.curve, public_key)
            pub_key.verify(signature, message, ec.ECDSA(hashes.SHA3_256()))
            return True
        except (InvalidSignature, ValueError):
            return False

    def hash_transaction(self, tx_data: dict) -> bytes:
        serialized = b''.join([
            tx_data['sender'],
            tx_data['receiver'],
            tx_data['amount'].to_bytes(64, 'big'),
            tx_data['nonce'].to_bytes(64, 'big')
        ])
        return hashlib.blake2b(serialized, digest_size=32).digest()
