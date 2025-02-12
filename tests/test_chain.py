import pytest
from src.blockchain.core.chain import Blockchain
from src.blockchain.core.block import Block, BlockHeader
import time

class TestBlockchain:
    def test_genesis_block(self, test_chain):
        assert test_chain.height == 0
        assert test_chain.last_block.header.previous_hash == b'\x00'*32

    def test_add_valid_block(self, test_chain):
        new_block = Block(
            BlockHeader(
                version=1,
                previous_hash=test_chain.last_block.hash,
                merkle_root=b'\x00'*32,
                timestamp=int(time.time()),
                difficulty=4,
                nonce=0
            ),
            transactions=[]
        )
        assert test_chain.add_block(new_block)
        assert test_chain.height == 1

    def test_invalid_block_prev_hash(self, test_chain):
        invalid_block = Block(
            BlockHeader(
                version=1,
                previous_hash=b'\xff'*32,
                merkle_root=b'\x00'*32,
                timestamp=int(time.time()),
                difficulty=4,
                nonce=0
            ),
            transactions=[]
        )
        assert not test_chain.add_block(invalid_block)

    def test_difficulty_adjustment(self, test_chain):
        original_diff = test_chain.difficulty
        test_chain.adjust_difficulty(60)  # Fast mining
        assert test_chain.difficulty == original_diff + 1
        
        test_chain.adjust_difficulty(600)  # Slow mining
        assert test_chain.difficulty == original_diff

    def test_chain_validation(self, test_chain):
        assert test_chain.is_valid_chain(test_chain.chain)
        
        # Tamper with chain
        tampered_chain = test_chain.chain.copy()
        tampered_chain[1] = Block(
            BlockHeader(
                version=1,
                previous_hash=tampered_chain[0].hash,
                merkle_root=b'\xff'*32,
                timestamp=int(time.time()),
                difficulty=4,
                nonce=0
            ),
            transactions=[]
        )
        assert not test_chain.is_valid_chain(tampered_chain)
