from dataclasses import dataclass
import hashlib
import time

@dataclass
class BlockHeader:
    version: int
    previous_hash: bytes
    merkle_root: bytes
    timestamp: float
    difficulty: int
    nonce: int = 0

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

@dataclass
class Block:
    header: BlockHeader
    transactions: list

    @property
    def hash(self) -> bytes:
        return self.header.hash()
