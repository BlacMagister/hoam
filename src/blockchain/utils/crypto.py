import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from typing import Tuple

def generate_ec_keypair() -> Tuple[ec.EllipticCurvePrivateKey, bytes]:
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint
    )
    return private_key, public_key

def derive_shared_secret(private_key: ec.EllipticCurvePrivateKey, peer_public_key: bytes) -> bytes:
    peer_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), peer_public_key)
    shared_key = private_key.exchange(ec.ECDH(), peer_key)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'blockchain-key-derivation',
    ).derive(shared_key)
