from typing import Dict, Set, List
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
            for tx in block_transactions:
                # Remove inputs
                for vin in tx['inputs']:
                    self._remove_utxo(vin['txid'], vin['vout'])
                
                # Add outputs
                for vout in tx['outputs']:
                    self._add_utxo(tx['id'], vout)

    def _add_utxo(self, txid: str, vout: dict):
        address = vout['address']
        if address not in self.utxo:
            self.utxo[address] = {}
        self.utxo[address][f"{txid}:{vout['n']}"] = vout['value']

    def _remove_utxo(self, txid: str, vout_index: int):
        key = f"{txid}:{vout_index}"
        for address in self.utxo:
            if key in self.utxo[address]:
                del self.utxo[address][key]
                if not self.utxo[address]:
                    del self.utxo[address]
                return

    def get_balance(self, address: str) -> float:
        with self.lock:
            return sum(self.utxo.get(address, {}).values())

    def find_spendable(self, address: str, amount: float) -> Dict[str, float]:
        with self.lock:
            unspent = self.utxo.get(address, {})
            selected = {}
            total = 0.0
            
            for txid_vout, value in unspent.items():
                selected[txid_vout] = value
                total += value
                if total >= amount:
                    break
                    
            return selected if total >= amount else {}
