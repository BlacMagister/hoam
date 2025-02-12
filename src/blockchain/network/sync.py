import asyncio
from typing import List, Dict, Optional
from .core.block import Block
from .core.chain import Blockchain
from .utils.logger import get_logger
from .network.p2p import P2PNetwork

logger = get_logger(__name__)

class ChainSynchronizer:
    def __init__(self, blockchain: Blockchain, network: P2PNetwork):
        self.blockchain = blockchain
        self.network = network
        self.syncing = False
        self.peer_chains = {}

    async def full_sync(self):
        if self.syncing:
            logger.info("Synchronization already in progress")
            return
        self.syncing = True

        try:
            logger.info("Starting full blockchain synchronization")
            longest_chain = await self.find_longest_valid_chain()
            if longest_chain:
                await self.replace_chain(longest_chain)
                logger.info("Blockchain synchronized successfully")
            else:
                logger.info("No valid chain found during synchronization")
        except Exception as e:
            logger.error(f"Error during synchronization: {e}")
        finally:
            self.syncing = False

    async def find_longest_valid_chain(self) -> Optional[List[Block]]:
        chains = await self.get_peer_chains()
        valid_chains = [chain for chain in chains if self.validate_chain(chain)]

        if not valid_chains:
            return None

        return max(valid_chains, key=len)

    async def get_peer_chains(self) -> List[List[Block]]:
        results = []
        for peer in self.network.peers:
            try:
                chain = await self.network.request_chain(peer)
                results.append(chain)
                logger.info(f"Received chain from peer {peer}")
            except Exception as e:
                logger.error(f"Failed to get chain from {peer}: {e}")
        return results

    def validate_chain(self, chain: List[Block]) -> bool:
        if len(chain) <= self.blockchain.height:
            logger.warning("Received chain is not longer than current chain")
            return False

        # Validate all blocks
        for i in range(1, len(chain)):
            if not self.blockchain.is_valid_block(chain[i]):
                logger.warning(f"Invalid block detected at height {i} in the chain")
                return False
        return True

    async def replace_chain(self, new_chain: List[Block]):
        # Handle chain reorganization
        current_height = self.blockchain.height
        new_height = len(new_chain) - 1

        if new_height > current_height:
            self.blockchain.chain = new_chain
            logger.info(f"Chain updated to height {new_height}")
