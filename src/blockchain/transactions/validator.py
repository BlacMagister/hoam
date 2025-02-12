from typing import Dict, List
from ..core.block import Block
from ..utils.crypto import validate_signature, calculate_merkle_root
from ..utils.logger import get_logger
import hashlib

logger = get_logger(__name__)

class TransactionValidator:
    def __init__(self, utxo_set=None):
        self.utxo_set = utxo_set

    def validate_transaction(self, tx: Dict) -> bool:
        try:
            # Validate structure
            required_fields = {'inputs', 'outputs', 'id', 'signatures'}
            if not required_fields.issubset(tx.keys()):
                return False
                
            # Check transaction hash
            if tx['id'] != self.calculate_tx_hash(tx):
                return False
                
            # Validate inputs
            input_sum = 0.0
            for vin in tx['inputs']:
                if not self.validate_input(vin, tx['signatures']):
                    return False
                input_sum += self.utxo_set.get_output_value(
                    vin['txid'], 
                    vin['vout']
                )
                
            # Validate outputs
            output_sum = sum(vout['value'] for vout in tx['outputs'])
            if input_sum < output_sum:
                return False
                
            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def validate_block(self, block: Block) -> bool:
        # Validate block structure
        if not block.verify(block.header.difficulty):
            return False
            
        # Validate merkle root
        if block.header.merkle_root != calculate_merkle_root(block.transactions):
            return False
            
        # Validate all transactions
        coinbase_count = 0
        for tx in block.transactions:
            if tx['inputs'] == []:  # Coinbase transaction
                coinbase_count += 1
                continue
            if not self.validate_transaction(tx):
                return False
                
        return coinbase_count == 1

    @staticmethod
    def calculate_tx_hash(tx: Dict) -> str:
        tx_data = {
            'inputs': tx['inputs'],
            'outputs': tx['outputs']
        }
        return hashlib.blake2b(
            json.dumps(tx_data, sort_keys=True).encode(),
            digest_size=32
        ).hexdigest()

    def validate_input(self, vin: Dict, signatures: List[str]) -> bool:
        # Check signature and UTXO existence
        if not self.utxo_set.is_output_spendable(vin['txid'], vin['vout']):
            return False
            
        message = f"{vin['txid']}{vin['vout']}".encode()
        return validate_signature(
            vin['pubkey'],
            message,
            signatures[vin['index']]
        )
