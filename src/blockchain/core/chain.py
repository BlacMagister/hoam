import time
import logging
from typing import List
from .block import Block, BlockHeader

logger = logging.getLogger(__name__)

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        try:
            genesis_header = BlockHeader(
                version=1,
                previous_hash=b'\x00'*32,
                merkle_root=b'\x00'*32,
                timestamp=int(time.time()),  # Ensure the timestamp is an integer
                difficulty=0
            )
            genesis_block = Block(
                version=genesis_header.version,
                previous_hash=genesis_header.previous_hash,
                merkle_root=genesis_header.merkle_root,
                timestamp=genesis_header.timestamp,
                difficulty=genesis_header.difficulty,
                nonce=genesis_header.nonce,
                signature=genesis_header.signature,
                transactions=[],
                validator_pubkey=b''
            )
            self.chain.append(genesis_block)
            logger.info("Genesis block created successfully")
        except Exception as e:
            logger.error(f"Error in creating genesis block: {e}")
            raise

    @property
    def last_block(self) -> Block:
        return self.chain[-1]
