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
        if height < 0 or height > self.blockchain.height:
            return {"error": "Invalid block height"}
        return self.blockchain.chain[height].serialize()

    @method
    async def submit_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        if self.mempool.add_transaction(tx):
            return {"status": "accepted"}
        return {"status": "rejected"}

    @method
    async def get_network_info(self) -> Dict[str, Any]:
        return {
            "height": self.blockchain.height,
            "difficulty": self.blockchain.difficulty,
            "mempool_size": len(self.mempool)
        }

async def rpc_handler(request):
    service = request.app['rpc_service']
    request = await request.text()
    response = await async_dispatch(request, methods=service)
    return web.json_response(response)

def setup_rpc(app: web.Application, blockchain: Blockchain, mempool: Mempool):
    app['rpc_service'] = JSONRPCService(blockchain, mempool)
    app.add_routes([web.post('/rpc', rpc_handler)])
