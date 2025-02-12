import hashlib
import time
from dataclasses import dataclass
from typing import List
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    signature: bytes

    def validate(self) -> bool:
        if self.sender == "GENESIS":
            return True
        try:
            public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), bytes.fromhex(self.sender))
            public_key.verify(
                self.signature,
                f"{self.sender}{self.receiver}{self.amount}".encode(),
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
        return hashlib.sha3_256(data.encode()).hexdigest()

class Block:
    def __init__(self, header: BlockHeader, transactions: List[Transaction]):
        self.header = header
        self.transactions = transactions
        self.hash = header.hash()

    def calculate_merkle_root(self) -> str:
        tx_hashes = [hashlib.sha3_256(f"{tx.sender}{tx.receiver}{tx.amount}".encode()).hexdigest() for tx in self.transactions]
        
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            tx_hashes = [hashlib.sha3_256(f"{a}{b}".encode()).hexdigest() for a, b in zip(tx_hashes[::2], tx_hashes[1::2])]
        
        return tx_hashes[0] if tx_hashes else "0" * 64

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.mempool: List[Transaction] = []
        self.difficulty = 4
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis_tx = Transaction("GENESIS", "0"*64, 1000000, b'')
        genesis_header = BlockHeader(
            version=1,
            previous_hash="0"*64,
            merkle_root=hashlib.sha3_256(b"genesis").hexdigest(),
            timestamp=time.time(),
            difficulty=0
        )
        self.chain.append(Block(genesis_header, [genesis_tx]))

    def add_transaction(self, tx: Transaction) -> bool:
        if tx.validate() and tx not in self.mempool:
            self.mempool.append(tx)
            return True
        return False

    def mine_block(self, miner_address: str) -> None:
        if not self.mempool:
            return

        reward_tx = Transaction("GENESIS", miner_address, 10.0, b'')
        transactions = [reward_tx] + self.mempool
        merkle_root = Block(BlockHeader(0, "", "", 0, 0), transactions).calculate_merkle_root()

        new_header = BlockHeader(
            version=1,
            previous_hash=self.chain[-1].hash,
            merkle_root=merkle_root,
            timestamp=time.time(),
            difficulty=self.difficulty
        )

        while True:
            new_header.nonce += 1
            block_hash = new_header.hash()
            if block_hash.startswith("0" * self.difficulty):
                self.chain.append(Block(new_header, transactions))
                self.mempool = []
                return
