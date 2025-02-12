import hashlib
import time
from dataclasses import dataclass
from typing import List, Dict
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_public_key

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    signature: str
    timestamp: float = time.time()

    def hash(self) -> str:
        return hashlib.sha3_256(
            f"{self.sender}{self.receiver}{self.amount}{self.timestamp}".encode()
        ).hexdigest()

    def validate(self) -> bool:
        if self.sender == "GENESIS":
            return True
        try:
            pub_key = load_pem_public_key(self.sender.encode())
            pub_key.verify(
                bytes.fromhex(self.signature),
                self.hash().encode(),
                ec.ECDSA(hashes.SHA256())
            )
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
    nonce: int = 0

    def hash(self) -> str:
        data = f"{self.version}{self.previous_hash}{self.merkle_root}{self.timestamp}{self.difficulty}{self.nonce}"
        return hashlib.blake2b(data.encode(), digest_size=32).hexdigest()

class Block:
    def __init__(self, header: BlockHeader, transactions: List[Transaction]):
        self.header = header
        self.transactions = transactions
        self.hash = header.hash()

    def calculate_merkle_root(self) -> str:
        tx_hashes = [tx.hash() for tx in self.transactions]
        while len(tx_hashes) > 1:
            tx_hashes = [hashlib.sha3_256(f"{a}{b}".encode()).hexdigest() 
                        for a, b in zip(tx_hashes[::2], tx_hashes[1::2])]
        return tx_hashes[0] if tx_hashes else "0"*64

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.mempool: Dict[str, Transaction] = {}
        self.difficulty = 4
        self._create_genesis()

    def _create_genesis(self):
        genesis_tx = Transaction(
            "GENESIS",
            "0"*64,
            1000000,
            ""
        )
        genesis_header = BlockHeader(
            version=1,
            previous_hash="0"*64,
            merkle_root=genesis_tx.hash(),
            timestamp=time.time(),
            difficulty=0
        )
        self.chain.append(Block(genesis_header, [genesis_tx]))

    def add_transaction(self, tx: Transaction) -> bool:
        if tx.validate() and tx.hash() not in self.mempool:
            self.mempool[tx.hash()] = tx
            return True
        return False

    def mine_block(self, miner_address: str) -> Block:
        if not self.mempool:
            return None

        reward_tx = Transaction(
            "GENESIS",
            miner_address,
            10.0,
            ""
        )
        transactions = [reward_tx] + list(self.mempool.values())
        
        header = BlockHeader(
            version=1,
            previous_hash=self.chain[-1].hash,
            merkle_root=Block(None, transactions).calculate_merkle_root(),
            timestamp=time.time(),
            difficulty=self.difficulty
        )

        while True:
            header.nonce += 1
            block_hash = header.hash()
            if block_hash.startswith("0" * self.difficulty):
                new_block = Block(header, transactions)
                self.chain.append(new_block)
                self.mempool.clear()
                return new_block
