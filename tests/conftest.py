import pytest
import sys
import os

# Tambahkan path ke direktori src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from blockchain.core.chain import Blockchain
from blockchain.core.block import Block, BlockHeader

@pytest.fixture
def test_chain():
    return Blockchain()

@pytest.fixture
def genesis_block(test_chain):
    return test_chain.chain[0]
