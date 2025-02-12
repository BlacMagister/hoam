import pytest
from src.blockchain.network.p2p import P2PNetwork
from src.blockchain.utils.config import ConfigLoader

@pytest.fixture
def test_config():
    config = ConfigLoader()
    config.config = {
        'network': {
            'listen_addr': '/ip4/127.0.0.1/tcp/0',
            'bootstrap_nodes': []
        }
    }
    return config

@pytest.mark.asyncio
async def test_p2p_bootstrapping(test_config):
    network = P2PNetwork(test_config)
    await network.start()
    assert len(network.peers) == 0
    await network.stop()
