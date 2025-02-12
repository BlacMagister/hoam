from typing import Dict, List
from ..core.block import Block
from ..utils.crypto import validate_signature, calculate_merkle_root
from ..utils.logger import get_logger
import hashlib
import json

logger = get_logger(__name__)

class TransactionValidator:
    def __init__(self, utxo_set=None):
        self.utxo_set = utxo_set

    def validate_transaction(self, tx: Dict) -> bool:
        try:
            # Validasi struktur transaksi
            required_fields = {'inputs', 'outputs', 'id', 'signatures'}
            if not required_fields.issubset(tx.keys()):
                logger.warning("Transaksi tidak memiliki field yang diperlukan")
                return False
                
            # Cek hash transaksi
            if tx['id'] != self.calculate_tx_hash(tx):
                logger.warning("Hash transaksi tidak valid")
                return False
                
            # Validasi input
            input_sum = 0.0
            for vin in tx['inputs']:
                if not self.validate_input(vin, tx['signatures']):
                    logger.warning("Input transaksi tidak valid")
                    return False
                input_sum += self.utxo_set.get_output_value(
                    vin['txid'], 
                    vin['vout']
                )
                
            # Validasi output
            output_sum = sum(vout['value'] for vout in tx['outputs'])
            if input_sum < output_sum:
                logger.warning("Jumlah input lebih kecil dari output")
                return False
                
            logger.info("Transaksi valid")
            return True
        except Exception as e:
            logger.error(f"Error saat validasi transaksi: {e}")
            return False

    def validate_block(self, block: Block) -> bool:
        try:
            # Validasi struktur block
            if not block.verify(block.header.difficulty):
                logger.warning("Block tidak valid berdasarkan proof of work")
                return False
                
            # Validasi merkle root
            if block.header.merkle_root != calculate_merkle_root(block.transactions):
                logger.warning("Merkle root block tidak valid")
                return False
                
            # Validasi semua transaksi
            coinbase_count = 0
            for tx in block.transactions:
                if tx['inputs'] == []:  # Transaksi coinbase
                    coinbase_count += 1
                    continue
                if not self.validate_transaction(tx):
                    logger.warning("Transaksi dalam block tidak valid")
                    return False
                    
            valid = coinbase_count == 1
            if not valid:
                logger.warning("Jumlah transaksi coinbase tidak valid")
            logger.info("Block valid")
            return valid
        except Exception as e:
            logger.error(f"Error saat validasi block: {e}")
            return False

    @staticmethod
    def calculate_tx_hash(tx: Dict) -> str:
        try:
            tx_data = {
                'inputs': tx['inputs'],
                'outputs': tx['outputs']
            }
            tx_hash = hashlib.blake2b(
                json.dumps(tx_data, sort_keys=True).encode(),
                digest_size=32
            ).hexdigest()
            return tx_hash
        except Exception as e:
            logger.error(f"Error saat menghitung hash transaksi: {e}")
            raise

    def validate_input(self, vin: Dict, signatures: List[str]) -> bool:
        try:
            # Cek signature dan keberadaan UTXO
            if not self.utxo_set.is_output_spendable(vin['txid'], vin['vout']):
                logger.warning(f"UTXO tidak dapat digunakan: {vin['txid']}:{vin['vout']}")
                return False
                
            message = f"{vin['txid']}{vin['vout']}".encode()
            valid = validate_signature(
                vin['pubkey'],
                message,
                signatures[vin['index']]
            )
            if not valid:
                logger.warning("Signature input transaksi tidak valid")
            return valid
        except Exception as e:
            logger.error(f"Error saat validasi input transaksi: {e}")
            return False
