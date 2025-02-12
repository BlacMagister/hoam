from jsonrpcserver import method, async_dispatch
from aiohttp import web
from typing import Any, Dict
from ..core.chain import Blockchain
from ..transactions.pool import Mempool
from ..utils.logger import get_logger

logger = get_logger(__name__)

class JSONRPCService:
    def __init__(self, blockchain: Blockchain, mempool: Mempool):
        self.blockchain = blockchain
        self.mempool = mempool

    @method
    async def get_block(self, height: int) -> Dict[str, Any]:
        try:
            if height < 0 or height > self.blockchain.height:
                logger.warning(f"Invalid block height requested: {height}")
                return {"error": "Invalid block height"}
            block_data = self.blockchain.chain[height].serialize()
            logger.info(f"Block data retrieved for height {height}")
            return block_data
        except Exception as e:
            logger.error(f"Error retrieving block data: {e}")
            return {"error": "Internal server error"}

    @method
    async def submit_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if self.mempool.add_transaction(tx):
                logger.info("Transaction accepted")
                return {"status": "accepted"}
            logger.warning("Transaction rejected")
            return {"status": "rejected"}
        except Exception as e:
            logger.error(f"Error submitting transaction: {e}")
            return {"status": "error", "message": str(e)}

    @method
    async def get_network_info(self) -> Dict[str, Any]:
        try:
            network_info = {
                "height": self.blockchain.height,
                "difficulty": self.blockchain.difficulty,
                "mempool_size": len(self.mempool)
            }
            logger.info("Network info retrieved")
            return network_info
        except Exception as e:
            logger.error(f"Error retrieving network info: {e}")
            return {"error": "Internal server error"}

async def rpc_handler(request):
    service = request.app['rpc_service']
    request_text = await request.text()
    response = await async_dispatch(request_text, methods=service)
    return web.json_response(response)

def setup_rpc(app: web.Application, blockchain: Blockchain, mempool: Mempool):
    app['rpc_service'] = JSONRPCService(blockchain, mempool)
    app.add_routes([web.post('/rpc', rpc_handler)])
