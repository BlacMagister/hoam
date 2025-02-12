import hashlib
import logging
from dataclasses import dataclass, field
from typing import List
from fastecdsa import curve, ecdsa
from fastecdsa.keys import import_key

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class BlockHeader:
    version: int
    previous_hash: bytes
    merkle_root: bytes
    timestamp: int
    difficulty: int
    nonce: int = 0
    signature: bytes = b''  # For PoA consensus

    def hash(self) -> bytes:
        try:
            data = b''.join([
                self.version.to_bytes(4, 'big'),
                self.previous_hash,
                self.merkle_root,
                self.timestamp.to_bytes(8, 'big'),
                self.difficulty.to_bytes(4, 'big'),
                self.nonce.to_bytes(8, 'big'),
                self.signature
            ])
            return hashlib.blake3(data).digest()
        except Exception as e:
            logger.error(f"Error in hashing block header: {e}")
            raise

@dataclass
class Block(BlockHeader):
    transactions: List['Transaction'] = field(default_factory=list)
    validator_pubkey: bytes = b''

    def verify(self) -> bool:
        try:
            pubkey = import_key(self.validator_pubkey)
            valid = ecdsa.verify(
                self.signature,
                self.hash(),
                pubkey,
                curve=curve.secp256k1
            )
            if valid:
                logger.info("Block verified successfully")
            else:
                logger.warning("Block verification failed")
            return valid
        except Exception as e:
            logger.error(f"Error in verifying block: {e}")
            return False
