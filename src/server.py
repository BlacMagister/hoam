from aiohttp import web
import asyncio
from blockchain import Blockchain, Block, Transaction
import json
import time

class Node:
    def __init__(self):
        self.app = web.Application()
        self.blockchain = Blockchain()
        self.peers = set()
        
        self.app.add_routes([
            web.get('/chain', self.get_chain),
            web.post('/tx', self.new_transaction),
            web.post('/mine', self.mine_block),
            web.get('/stats', self.get_stats),
            web.post('/peers', self.add_peers)
        ])

    async def get_chain(self, request):
        return web.json_response([
            {
                "hash": block.hash,
                "height": idx,
                "transactions": len(block.transactions)
            } for idx, block in enumerate(self.blockchain.chain)
        ])

    async def new_transaction(self, request):
        data = await request.json()
        tx = Transaction(
            data['sender'],
            data['receiver'],
            data['amount'],
            data['signature']
        )
        if self.blockchain.add_transaction(tx):
            await self.broadcast('/tx', data)
            return web.json_response({"status": "accepted"})
        return web.json_response({"status": "rejected"}, status=400)

    async def mine_block(self, request):
        data = await request.json()
        miner = data.get('miner')
        if not miner:
            return web.json_response({"error": "Miner address required"}, status=400)
        
        start_time = time.time()
        new_block = self.blockchain.mine_block(miner)
        mining_time = time.time() - start_time
        
        if new_block:
            await self.broadcast('/block', new_block.__dict__)
            return web.json_response({
                "hash": new_block.hash,
                "height": len(self.blockchain.chain),
                "mining_time": mining_time
            })
        return web.json_response({"error": "Mining failed"}, status=500)

    async def broadcast(self, endpoint, data):
        for peer in self.peers:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(f"http://{peer}{endpoint}", json=data)
            except:
                self.peers.discard(peer)

    async def get_stats(self, request):
        return web.json_response({
            "height": len(self.blockchain.chain),
            "difficulty": self.blockchain.difficulty,
            "mempool": len(self.blockchain.mempool)
        })

    async def add_peers(self, request):
        new_peers = await request.json()
        self.peers.update(new_peers)
        return web.json_response({"peers": list(self.peers)})

    async def run(self, host='0.0.0.0', port=8080):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        print(f"⚡ Node running on {host}:{port}")
        await asyncio.Event().wait()

if __name__ == "__main__":
    node = Node()
    asyncio.run(node.run())
