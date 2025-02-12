import pytest
from hypothesis import given, strategies as st
from src.blockchain.core.chain import Blockchain
from src.blockchain.transactions.validator import TransactionValidator

class TestSecurity:
    @pytest.mark.parametrize("malicious_input", [
        "'; DROP TABLE blocks;--", 
        "<script>alert('hack')</script>",
        b'\x80\x00\x00\x00'  # Invalid binary
    ])
    def test_sql_injection(self, malicious_input):
        """Test resistensi SQL injection"""
        chain = Blockchain()
        with pytest.raises(ValueError):
            chain.add_block(malicious_input)

    @given(st.binary())
    def test_signature_forgery(self, fake_signature):
        """Property-based test untuk signature palsu"""
        validator = TransactionValidator()
        assert not validator.validate_signature(
            public_key="invalid_pubkey",
            message=b"hello",
            signature=fake_signature
        )

    def test_double_spend_attack(self):
        """Simulasi serangan double spend"""
        utxo = UTXOSet()
        utxo.update([{'id': 'tx1', 'outputs': [{'address': 'A', 'value': 10}]}])
        
        # Coba spend output yang sama 2x
        tx1 = {'inputs': [{'txid': 'tx1', 'vout': 0}], 'outputs': [...]}
        tx2 = {'inputs': [{'txid': 'tx1', 'vout': 0}], 'outputs': [...]}
        
        assert utxo.apply_transaction(tx1)
        assert not utxo.apply_transaction(tx2)

    def test_sybil_attack_resistance(self):
        """Test resistensi terhadap serangan node palsu"""
        from src.blockchain.network.p2p import NetworkManager
        
        network = NetworkManager()
        for _ in range(1000):
            network.connect_fake_node()
        
        assert len(network.peers) < 50  # Auto-reject >50 node

    def test_tampered_block(self):
        """Test deteksi blok yang diubah"""
        chain = Blockchain()
        valid_block = chain.mine_block()
        
        # Ubah hash transaksi
        tampered_block = valid_block.copy()
        tampered_block.transactions[0]['amount'] = 1000000
        
        assert not chain.validate_block(tampered_block)
