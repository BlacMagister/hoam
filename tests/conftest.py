import pytest
from src.blockchain.core.chain import Blockchain
from src.blockchain.core.block import Block, BlockHeader
from src.blockchain.transactions.pool import Mempool
from src.blockchain.transactions.utxo import UTXOSet
from src.blockchain.wallet.signer import TransactionSigner
from datetime import datetime

@pytest.fixture(scope="session")
def test_chain():
    return Blockchain()

@pytest.fixture
def genesis_block():
    return Block(
        BlockHeader(
            version=1,
            previous_hash=b'\x00'*32,
            merkle_root=b'\x00'*32,
            timestamp=int(datetime.now().timestamp()),
            difficulty=0,
            nonce=0
        ),
        transactions=[]
    )

@pytest.fixture
def sample_transaction():
    signer = TransactionSigner()
    _, pub_key = signer.generate_keypair()
    return {
        "inputs": [],
        "outputs": [{"address": pub_key.hex(), "value": 10.0}],
        "signatures": []
    }

@pytest.fixture
def test_mempool():
    return Mempool()

@pytest.fixture
def test_utxo():
    return UTXOSet()
