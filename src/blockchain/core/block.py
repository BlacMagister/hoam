import hashlib
import time
from dataclasses import dataclass
from typing import List, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

@dataclass(frozen=True)
class BlockHeader:
    version: int
    previous_hash: bytes
    merkle_root: bytes
    timestamp: float
    difficulty: int
    nonce: int
    miner: bytes  # Public key miner
    
    def hash(self) -> bytes:
        data = b''.join([
            self.version.to_bytes(4, 'big'),
            self.previous_hash,
            self.merkle_root,
            int(self.timestamp).to_bytes(8, 'big'),
            self.difficulty.to_bytes(4, 'big'),
            self.nonce.to_bytes(8, 'big'),
            self.miner
        ])
        return hashlib.blake2b(data, digest_size=32).digest()
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "previous_hash": self.previous_hash.hex(),
            "merkle_root": self.merkle_root.hex(),
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "miner": self.miner.hex()
        }

@dataclass(frozen=True)
class Block:
    header: BlockHeader
    transactions: List[Dict[str, Any]]
    
    @property
    def hash(self) -> bytes:
        return self.header.hash()
    
    def verify_pow(self) -> bool:
        target = int.from_bytes(b'\x00' * self.header.difficulty, 'big')
        return int.from_bytes(self.hash, 'big') < target
    
    def get_miner_address(self) -> str:
        public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256K1(), 
            self.header.miner
        )
        return public_key.public_bytes(
            Encoding.X962,
            PublicFormat.CompressedPoint
        ).hex()
