from fastecdsa import ecdsa, keys, curve
from hashlib import blake2b
from typing import Tuple
from .logger import get_logger

logger = get_logger(__name__)

def generate_keypair() -> Tuple[str, str]:
    """Generate ECDSA keypair using secp256k1"""
    try:
        priv_key, pub_key = keys.gen_keypair(curve.secp256k1)
        priv_key_serialized = keys.serialize_private_key(priv_key, curve=curve.secp256k1)
        pub_key_serialized = keys.serialize_public_key(pub_key, curve=curve.secp256k1)
        logger.info("Keypair berhasil di-generate")
        return (priv_key_serialized, pub_key_serialized)
    except Exception as e:
        logger.error(f"Error saat generate keypair: {e}")
        raise

def sign_data(private_key: str, data: bytes) -> bytes:
    """Sign data with deterministic ECDSA"""
    try:
        signature = ecdsa.sign(data, private_key, curve=curve.secp256k1, hashfunc=blake2b)
        logger.info("Data berhasil ditandatangani")
        return signature
    except Exception as e:
        logger.error(f"Error saat menandatangani data: {e}")
        raise

def validate_signature(public_key: str, data: bytes, signature: bytes) -> bool:
    """Verify signature with error handling"""
    try:
        valid = ecdsa.verify(signature, data, public_key, curve=curve.secp256k1)
        logger.info(f"Signature valid: {valid}")
        return valid
    except Exception as e:
        logger.error(f"Error saat memverifikasi signature: {e}")
        return False
