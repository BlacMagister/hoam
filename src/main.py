import asyncio
from .blockchain.core.chain import Blockchain
from .blockchain.network.p2p import P2PNetwork
from .blockchain.api.rest import run_api

async def main():
    blockchain = Blockchain()
    network = P2PNetwork(config={
        'listen_addr': '/ip4/0.0.0.0/tcp/4001',
        'bootstrap_nodes': []
    })
    
    await network.start()
    run_api()

if __name__ == '__main__':
    asyncio.run(main())
