import hashlib
import time
from dataclasses import dataclass
from typing import List
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

@dataclass(frozen=True)
class BlockHeader:
    version: int
    previous_hash: bytes
    merkle_root: bytes
    timestamp: float
    difficulty: int
    nonce: int

    def hash(self) -> bytes:
        data = b''.join([
            self.version.to_bytes(4, 'big'),
            self.previous_hash,
            self.merkle_root,
            int(self.timestamp).to_bytes(8, 'big'),
            self.difficulty.to_bytes(4, 'big'),
            self.nonce.to_bytes(8, 'big')
        ])
        return hashlib.blake2b(data, digest_size=32).digest()

@dataclass(frozen=True)
class Block:
    header: BlockHeader
    transactions: List['Transaction']

    @property
    def hash(self) -> bytes:
        return self.header.hash()

    def verify(self) -> bool:
        target = int.from_bytes(b'\x00' * self.header.difficulty, 'big')
        return int.from_bytes(self.hash, 'big') < target
