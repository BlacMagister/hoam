import pytest
from src.blockchain.core.consensus import ProofOfWork, ProofOfStake
from src.blockchain.core.block import BlockHeader

class TestConsensus:
    def test_pow_validation(self):
        pow = ProofOfWork(difficulty=4)
        valid_header = BlockHeader(
            version=1,
            previous_hash=b'\x00'*32,
            merkle_root=b'\x00'*32,
            timestamp=0,
            difficulty=4,
            nonce=12345
        )
        
        # Mine valid nonce
        valid_nonce = pow.mine_block(valid_header)
        valid_header.nonce = valid_nonce
        assert pow.validate(valid_header.hash())
        
        # Test invalid
        invalid_header = valid_header.copy()
        invalid_header.nonce += 1
        assert not pow.validate(invalid_header.hash())

    def test_pos_validation(self):
        validators = ["addr1", "addr2", "addr3"]
        pos = ProofOfStake(validators)
        seed = b'blockchain-seed'
        
        selected = pos.select_validator(seed)
        assert selected in validators
        
        # Test deterministic selection
        assert pos.select_validator(seed) == selected

    def test_hybrid_consensus(self):
        # Implement hybrid consensus scenario
        pass
