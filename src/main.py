import asyncio
import logging
from .blockchain.core.chain import Blockchain
from .blockchain.network.p2p import P2PNetwork
from .blockchain.api.rest import run_api

async def main():
    """
    Main entry point for the blockchain application.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Initialize blockchain and network
        blockchain = Blockchain()
        network = P2PNetwork(config={
            'listen_addr': '/ip4/0.0.0.0/tcp/4001',
            'bootstrap_nodes': []
        })

        # Start the network
        await network.start()
        logger.info("Network started successfully")

        # Run the API
        run_api()
        logger.info("API server is running")

    except Exception as e:
        logger.error(f"Error in main application: {e}")

if __name__ == '__main__':
    asyncio.run(main())
