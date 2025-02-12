from typing import Dict, List, Optional
from ..utils.crypto import validate_signature
from .validator import TransactionValidator
from ..wallet.signer import TransactionSigner
from ..utils.logger import get_logger
import hashlib
import json
import time

logger = get_logger(__name__)

class Mempool:
    def __init__(self, max_size: int = 50000):
        self.transactions: Dict[str, dict] = {}
        self.validator = TransactionValidator()
        self.max_size = max_size
        self.signature_checker = TransactionSigner()

    def add_transaction(self, tx: dict) -> bool:
        tx_hash = self._get_tx_hash(tx)

        if tx_hash in self.transactions:
            logger.info("Transaksi sudah ada di mempool")
            return False

        if not self.validator.validate(tx):
            logger.warning("Transaksi tidak valid")
            return False

        if not self.signature_checker.verify_signature(
            bytes.fromhex(tx['sender']),
            tx['message'].encode(),
            bytes.fromhex(tx['signature'])
        ):
            logger.warning("Signature transaksi tidak valid")
            return False

        if len(self.transactions) >= self.max_size:
            logger.info("Mempool penuh, menghapus transaksi tertua")
            self._evict_oldest()

        self.transactions[tx_hash] = {
            'tx': tx,
            'timestamp': time.time()
        }
        logger.info("Transaksi berhasil ditambahkan ke mempool")
        return True

    def _get_tx_hash(self, tx: dict) -> str:
        try:
            tx_hash = hashlib.blake2b(
                json.dumps(tx, sort_keys=True).encode(),
                digest_size=32
            ).hexdigest()
            return tx_hash
        except Exception as e:
            logger.error(f"Error saat menghitung hash transaksi: {e}")
            raise

    def _evict_oldest(self):
        try:
            oldest = min(self.transactions.items(), key=lambda x: x[1]['timestamp'])
            del self.transactions[oldest[0]]
            logger.info("Transaksi tertua berhasil dihapus dari mempool")
        except Exception as e:
            logger.error(f"Error saat menghapus transaksi tertua: {e}")
            raise

    def get_transactions(self, max_count: int = 1000) -> List[dict]:
        try:
            transactions = [tx['tx'] for tx in 
                            sorted(self.transactions.values(), 
                            key=lambda x: x['timestamp'])[:max_count]]
            return transactions
        except Exception as e:
            logger.error(f"Error saat mengambil transaksi dari mempool: {e}")
            raise

    def __len__(self):
        return len(self.transactions)
