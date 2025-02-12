import pytest
from pytest_benchmark.fixture import BenchmarkFixture
from src.blockchain.core.chain import Blockchain
from src.blockchain.transactions.pool import Mempool
from src.blockchain.utils.crypto import generate_keypair, sign_data
import time

@pytest.fixture(scope="module")
def highload_setup():
    """Generate 10,000 transactions for stress test"""
    mempool = Mempool()
    priv, pub = generate_keypair()
    
    transactions = []
    for i in range(10_000):
        tx = {
            'sender': pub,
            'receiver': 'recipient_addr',
            'amount': i % 100,
            'nonce': i
        }
        signature = sign_data(priv, str(tx).encode())
        transactions.append({**tx, 'signature': signature})
    
    return mempool, transactions

def test_tx_throughput(benchmark: BenchmarkFixture, highload_setup):
    """Test kemampuan memproses 10k transaksi/detik"""
    mempool, txs = highload_setup
    
    def _process_txs():
        for tx in txs:
            mempool.add_transaction(tx)
    
    benchmark(_process_txs)
    assert benchmark.stats['ops'] >= 9_500  # Min 9.5k TPS

def test_block_propagation(benchmark):
    """Test latency propagasi blok ke 100 node"""
    from src.blockchain.network.p2p import NetworkManager
    
    def _propagate():
        network = NetworkManager()
        return network.broadcast_block(block_data)
    
    result = benchmark(_propagate)
    assert result.latency < 0.5  # Max 500ms

def test_memory_usage():
    """Test konsumsi memori pada 100k transaksi"""
    import tracemalloc
    from src.blockchain.transactions.utxo import UTXOSet
    
    tracemalloc.start()
    
    utxo = UTXOSet()
    for i in range(100_000):
        utxo.update([{
            'id': f"tx{i}",
            'outputs': [{'address': 'addr', 'value': i}]
        }])
    
    current, peak = tracemalloc.get_traced_memory()
    assert peak < 100_000_000  # Max 100MB
