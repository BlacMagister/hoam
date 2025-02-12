from typing import List, Dict, Optional
from .block import Block, BlockHeader
from ..transactions.validator import TransactionValidator
from ..utils.crypto import calculate_merkle_root
import time

class Blockchain:
    def __init__(self, consensus_algorithm: str = 'pow'):
        self.chain: List[Block] = []
        self.unconfirmed_transactions: List[Dict] = []
        self.validator = TransactionValidator()
        self.difficulty = 4
        self.consensus_algorithm = consensus_algorithm
        self.init_genesis_block()

    def init_genesis_block(self):
        genesis_header = BlockHeader(
            version=1,
            previous_hash=b'\x00'*32,
            merkle_root=b'\x00'*32,
            timestamp=int(time.time()),
            difficulty=0,
            nonce=0
        )
        genesis_block = Block(genesis_header, [])
        self.chain.append(genesis_block)

    def add_block(self, block: Block) -> bool:
        if not self.is_valid_block(block):
            return False
        self.chain.append(block)
        return True

    def is_valid_block(self, block: Block) -> bool:
        last_block = self.last_block
        return (
            block.header.previous_hash == last_block.hash and
            block.verify(self.difficulty) and
            self.validator.validate_block_transactions(block.transactions)
        )

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    @property
    def height(self) -> int:
        return len(self.chain) - 1

    def adjust_difficulty(self, time_taken: float):
        target_block_time = 300  # 5 minutes
        if time_taken < target_block_time / 2:
            self.difficulty += 1
        elif time_taken > target_block_time * 2:
            self.difficulty = max(1, self.difficulty - 1)
