from typing import List
import hashlib

class ProofOfWork:
    def __init__(self, difficulty: int):
        self.difficulty = difficulty
        self.target = 2 ** (256 - difficulty)

    def validate(self, block_hash: bytes) -> bool:
        return int.from_bytes(block_hash, 'big') < self.target

    def mine_block(self, block_header: 'BlockHeader') -> int:
        nonce = 0
        while True:
            header = block_header.copy(update={'nonce': nonce})
            current_hash = header.hash()
            if self.validate(current_hash):
                return nonce
            nonce += 1

class ProofOfStake:
    def __init__(self, validators: List[str]):
        self.validators = validators

    def select_validator(self, seed: bytes) -> str:
        seed_hash = hashlib.sha256(seed).digest()
        index = int.from_bytes(seed_hash, 'big') % len(self.validators)
        return self.validators[index]
