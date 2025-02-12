from dataclasses import dataclass
from typing import List, Optional
import hashlib
import time
from cryptography.hazmat.primitives import hashes

@dataclass(frozen=True)
class BlockHeader:
    version: int
    previous_hash: bytes
    merkle_root: bytes
    timestamp: int
    difficulty: int
    nonce: int

    def hash(self) -> bytes:
        data = b''.join([
            self.version.to_bytes(4, 'big'),
            self.previous_hash,
            self.merkle_root,
            self.timestamp.to_bytes(8, 'big'),
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

    def verify(self, difficulty: int) -> bool:
        target = int.from_bytes(b'\x00' * (difficulty // 8) + b'\xff' * (32 - (difficulty // 8)), 'big')
        return int.from_bytes(self.hash, 'big') < target
