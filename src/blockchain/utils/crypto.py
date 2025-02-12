from fastecdsa import ecdsa, keys, curve
from hashlib import blake2b
from typing import Tuple

def generate_keypair() -> Tuple[str, str]:
    """Generate ECDSA keypair using secp256k1"""
    priv_key, pub_key = keys.gen_keypair(curve.secp256k1)
    return (
        keys.serialize_private_key(priv_key, curve=curve.secp256k1),
        keys.serialize_public_key(pub_key, curve=curve.secp256k1)
    )

def sign_data(private_key: str, data: bytes) -> bytes:
    """Sign data with deterministic ECDSA"""
    return ecdsa.sign(data, private_key, curve=curve.secp256k1, hashfunc=blake2b)

def validate_signature(public_key: str, data: bytes, signature: bytes) -> bool:
    """Verify signature with error handling"""
    try:
        return ecdsa.verify(signature, data, public_key, curve=curve.secp256k1)
    except:
        return False
