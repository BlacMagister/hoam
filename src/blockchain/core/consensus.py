from enum import Enum
import random

class ConsensusAlgorithm(Enum):
    POW = "proof_of_work"
    POS = "proof_of_stake"
    POA = "proof_of_authority"

class ConsensusEngine:
    def __init__(self, algorithm: ConsensusAlgorithm):
        self.algorithm = algorithm
    
    def validate_block(self, block: 'Block', validators: list) -> bool:
        if self.algorithm == ConsensusAlgorithm.POW:
            return self._validate_pow(block)
        elif self.algorithm == ConsensusAlgorithm.POS:
            return self._validate_pos(block, validators)
        elif self.algorithm == ConsensusAlgorithm.POA:
            return self._validate_poa(block, validators)
    
    def _validate_pow(self, block: 'Block') -> bool:
        return block.verify()
    
    def _validate_pos(self, block: 'Block', validators: list) -> bool:
        total_stake = sum(v['stake'] for v in validators)
        selection = random.uniform(0, total_stake)
        cumulative = 0
        for v in validators:
            cumulative += v['stake']
            if cumulative >= selection:
                return v['address'] == block.header.miner
        return False

    def _validate_poa(self, block: 'Block', validators: list) -> bool:
        current_index = len(blockchain) % len(validators)
        return validators[current_index] == block.header.miner
