import pytest
from src.blockchain.transactions.validator import TransactionValidator
from src.blockchain.transactions.utxo import UTXOSet
import time

class TestTransactions:
    def test_valid_transaction(self, sample_transaction, test_utxo):
        validator = TransactionValidator(test_utxo)
        assert validator.validate_transaction(sample_transaction)

    def test_double_spend(self, test_mempool, sample_transaction):
        # First add should succeed
        assert test_mempool.add_transaction(sample_transaction)
        
        # Second add should fail
        assert not test_mempool.add_transaction(sample_transaction)

    def test_mempool_eviction(self, test_mempool):
        # Fill mempool
        for i in range(1001):
            tx = {"inputs": [], "outputs": [], "timestamp": time.time()}
            test_mempool.add_transaction(tx)
        
        assert len(test_mempool) == 1000

    def test_utxo_management(self, test_utxo):
        test_utxo.update([{
            "id": "tx1",
            "outputs": [{"address": "addr1", "value": 5.0}]
        }])
        assert test_utxo.get_balance("addr1") == 5.0
        
        test_utxo.update([{
            "id": "tx2",
            "inputs": [{"txid": "tx1", "vout": 0}],
            "outputs": [{"address": "addr2", "value": 5.0}]
        }])
        assert test_utxo.get_balance("addr1") == 0.0
        assert test_utxo.get_balance("addr2") == 5.0

    def test_signature_validation(self, sample_transaction):
        validator = TransactionValidator()
        # Implement full signature validation test
        pass
