import hashlib
import time
import json
from dataclasses import dataclass
from typing import List, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_public_key

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    signature: bytes

    def hash(self) -> bytes:
        return hashlib.sha256(f"{self.sender}{self.receiver}{self.amount}".encode()).digest()

    def validate(self) -> bool:
        if self.sender == "GENESIS":
            return True
        try:
            pub_key = load_pem_public_key(self.sender.encode())
            pub_key.verify(self.signature, self.hash(), ec.ECDSA(hashes.SHA256()))
            return True
        except:
            return False

@dataclass
class BlockHeader:
    version: int
    previous_hash: str
    merkle_root: str
    timestamp: float
    difficulty: int
    nonce: int

    def hash(self) -> str:
        data = f"{self.version}{self.previous_hash}{self.merkle_root}{self.timestamp}{self.difficulty}{self.nonce}"
        return hashlib.sha3_256(data.encode()).hexdigest()

class Block:
    def __init__(self, header: BlockHeader, transactions: List[Transaction]):
        self.header = header
        self.transactions = transactions
        self.hash = header.hash()

    def calculate_merkle_root(self) -> str:
        hashes = [tx.hash().hex() for tx in self.transactions]
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            hashes = [hashlib.sha3_256(f"{a}{b}".encode()).hexdigest() for a, b in zip(hashes[::2], hashes[1::2])]
        return hashes[0]

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.mempool: List[Transaction] = []
        self.difficulty = 4
        self._create_genesis()

    def _create_genesis(self):
        genesis_tx = Transaction("GENESIS", "0"*64, 1000000, b'')
        genesis_header = BlockHeader(
            version=1,
            previous_hash="0"*64,
            merkle_root=genesis_tx.hash().hex(),
            timestamp=time.time(),
            difficulty=0,
            nonce=0
        )
        self.chain.append(Block(genesis_header, [genesis_tx]))

    def add_transaction(self, tx: Transaction) -> bool:
        if tx.validate() and tx not in self.mempool:
            self.mempool.append(tx)
            return True
        return False

    def mine_block(self, miner_address: str) -> Optional[Block]:
        if not self.mempool:
            return None

        reward_tx = Transaction("GENESIS", miner_address, 10.0, b'')
        transactions = [reward_tx] + self.mempool
        merkle_root = Block(None, transactions).calculate_merkle_root()

        previous_hash = self.chain[-1].hash
        header = BlockHeader(
            version=1,
            previous_hash=previous_hash,
            merkle_root=merkle_root,
            timestamp=time.time(),
            difficulty=self.difficulty,
            nonce=0
        )

        while True:
            header_hash = header.hash()
            if header_hash.startswith("0" * self.difficulty):
                block = Block(header, transactions)
                self.chain.append(block)
                self.mempool = []
                return block
            header.nonce += 1
