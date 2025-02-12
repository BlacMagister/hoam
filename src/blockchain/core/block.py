import hashlib
from dataclasses import dataclass
from typing import List
from fastecdsa import curve, ecdsa

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

class Block(BlockHeader):
    transactions: List['Transaction']

    def verify(self) -> bool:
        # Verify ECDSA signature for PoA
        return ecdsa.verify(
            self.signature,
            self.hash(),
            self.validator_pubkey,
            curve=curve.secp256k1
        )
