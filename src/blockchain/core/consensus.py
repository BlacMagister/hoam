import hashlib
import random
from enum import Enum
from typing import Dict, List
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

class ConsensusType(Enum):
    PROOF_OF_WORK = 1
    PROOF_OF_STAKE = 2
    DELEGATED_POS = 3

class ConsensusEngine:
    def __init__(self, consensus_type: ConsensusType, params: Dict):
        self.consensus_type = consensus_type
        self.params = params
        self.curve = ec.SECP256K1()
        
    def validate_block(self, block, chain_state: Dict) -> bool:
        if self.consensus_type == ConsensusType.PROOF_OF_WORK:
            return self._validate_pow(block)
        elif self.consensus_type == ConsensusType.PROOF_OF_STAKE:
            return self._validate_pos(block, chain_state)
        elif self.consensus_type == ConsensusType.DELEGATED_POS:
            return self._validate_dpos(block, chain_state)
    
    def _validate_pow(self, block) -> bool:
        target = int(self.params['difficulty'] * 'f', 16)
        block_hash = int(block.hash.hex(), 16)
        return block_hash < target
    
    def _validate_pos(self, block, chain_state: Dict) -> bool:
        public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            self.curve, 
            block.header.miner
        )
        staked_amount = chain_state['stakes'].get(public_key, 0)
        
        hash_with_stake = hashlib.sha3_256(
            block.hash + str(staked_amount).encode()
        ).digest()
        
        return int.from_bytes(hash_with_stake, 'big') < self.params['target'] * staked_amount
    
    def _validate_dpos(self, block, chain_state: Dict) -> bool:
        current_slot = int(block.header.timestamp // self.params['slot_duration'])
        delegates = chain_state['delegates']
        delegate_index = current_slot % len(delegates)
        return delegates[delegate_index] == block.header.miner.hex()

    def select_validator(self, chain_state: Dict) -> bytes:
        if self.consensus_type == ConsensusType.PROOF_OF_STAKE:
            total_stake = sum(chain_state['stakes'].values())
            selection = random.uniform(0, total_stake)
            cumulative = 0
            for pub_key, stake in chain_state['stakes'].items():
                cumulative += stake
                if cumulative >= selection:
                    return pub_key
        elif self.consensus_type == ConsensusType.DELEGATED_POS:
            current_time = time.time()
            slot = int(current_time // self.params['slot_duration'])
            return chain_state['delegates'][slot % len(chain_state['delegates'])]
        return b''
