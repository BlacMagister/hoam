from .block import Block, BlockHeader
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis_header = BlockHeader(
            version=1,
            previous_hash=b'\x00'*32,
            merkle_root=b'\x00'*32,
            timestamp=time.time(),
            difficulty=0
        )
        self.chain.append(Block(genesis_header, []))
    
    @property
    def last_block(self) -> Block:
        return self.chain[-1]
