from typing import Dict, List
from ..utils.crypto import hash_public_key
from ..utils.logger import get_logger
import threading

logger = get_logger(__name__)

class UTXOSet:
    def __init__(self):
        self.utxo: Dict[str, Dict[str, float]] = {}
        self.lock = threading.RLock()

    def update(self, block_transactions: List[dict]):
        with self.lock:
            try:
                for tx in block_transactions:
                    # Remove inputs
                    for vin in tx['inputs']:
                        self._remove_utxo(vin['txid'], vin['vout'])
                    
                    # Add outputs
                    for vout in tx['outputs']:
                        self._add_utxo(tx['id'], vout)
                logger.info("UTXOSet berhasil diperbarui")
            except Exception as e:
                logger.error(f"Error saat memperbarui UTXOSet: {e}")
                raise

    def _add_utxo(self, txid: str, vout: dict):
        try:
            address = vout['address']
            if address not in self.utxo:
                self.utxo[address] = {}
            self.utxo[address][f"{txid}:{vout['n']}"] = vout['value']
            logger.info(f"UTXO ditambahkan untuk txid: {txid}, vout: {vout['n']}")
        except Exception as e:
            logger.error(f"Error saat menambahkan UTXO: {e}")
            raise

    def _remove_utxo(self, txid: str, vout_index: int):
        try:
            key = f"{txid}:{vout_index}"
            for address in self.utxo:
                if key in self.utxo[address]:
                    del self.utxo[address][key]
                    if not self.utxo[address]:
                        del self.utxo[address]
                    logger.info(f"UTXO dihapus untuk txid: {txid}, vout_index: {vout_index}")
                    return
        except Exception as e:
            logger.error(f"Error saat menghapus UTXO: {e}")
            raise

    def get_balance(self, address: str) -> float:
        with self.lock:
            try:
                balance = sum(self.utxo.get(address, {}).values())
                logger.info(f"Saldo untuk {address}: {balance}")
                return balance
            except Exception as e:
                logger.error(f"Error saat mengambil saldo: {e}")
                raise

    def find_spendable(self, address: str, amount: float) -> Dict[str, float]:
        with self.lock:
            try:
                unspent = self.utxo.get(address, {})
                selected = {}
                total = 0.0
                
                for txid_vout, value in unspent.items():
                    selected[txid_vout] = value
                    total += value
                    if total >= amount:
                        break
                        
                if total >= amount:
                    logger.info(f"UTXO yang dapat digunakan ditemukan untuk {address}: {selected}")
                    return selected
                else:
                    logger.warning(f"Saldo tidak mencukupi untuk {address}")
                    return {}
            except Exception as e:
                logger.error(f"Error saat mencari UTXO yang dapat digunakan: {e}")
                raise
