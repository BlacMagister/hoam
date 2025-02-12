from typing import List
import hashlib
import logging

logger = logging.getLogger(__name__)

class ProofOfWork:
    def __init__(self, difficulty: int):
        self.difficulty = difficulty
        self.target = 2 ** (256 - difficulty)

    def validate(self, block_hash: bytes) -> bool:
        try:
            is_valid = int.from_bytes(block_hash, 'big') < self.target
            logger.info(f"Block hash validation: {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"Error in PoW validation: {e}")
            return False

    def mine_block(self, block_header: 'BlockHeader') -> int:
        nonce = 0
        try:
            while True:
                header = block_header.copy(update={'nonce': nonce})
                current_hash = header.hash()
                if self.validate(current_hash):
                    logger.info(f"Block mined successfully with nonce: {nonce}")
                    return nonce
                nonce += 1
        except Exception as e:
            logger.error(f"Error in mining block: {e}")
            raise

class ProofOfStake:
    def __init__(self, validators: List[str]):
        self.validators = validators

    def select_validator(self, seed: bytes) -> str:
        try:
            seed_hash = hashlib.sha256(seed).digest()
            index = int.from_bytes(seed_hash, 'big') % len(self.validators)
            validator = self.validators[index]
            logger.info(f"Validator selected: {validator}")
            return validator
        except Exception as e:
            logger.error(f"Error in selecting validator: {e}")
            raise
