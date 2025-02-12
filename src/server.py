from aiohttp import web
import aiohttp
import asyncio
from blockchain import Blockchain, Transaction, Block
from cryptography.hazmat.primitives import serialization
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
            web.get('/peers', self.get_peers),
            web.post('/peers', self.add_peers)
        ])

    async def get_chain(self, request):
        return web.json_response([{
            "index": block.header.version,
            "hash": block.hash,
            "previous_hash": block.header.previous_hash,
            "transactions": len(block.transactions)
        } for block in self.blockchain.chain])

    async def new_transaction(self, request):
        data = await request.json()
        try:
            tx = Transaction(
                data['sender'],
                data['receiver'],
                float(data['amount']),
                bytes.fromhex(data['signature'])
            )
            if self.blockchain.add_transaction(tx):
                await self.broadcast(f"/tx", data)
                return web.json_response({"status": "TX added to mempool"})
            return web.json_response({"error": "Invalid TX"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    async def mine_block(self, request):
        data = await request.json()
        miner = data.get('miner', '')
        if not miner:
            return web.json_response({"error": "Miner address required"}, status=400)
        
        self.blockchain.mine_block(miner)
        last_block = self.blockchain.chain[-1]
        await self.broadcast("/block", last_block.__dict__)
        return web.json_response({
            "index": last_block.header.version,
            "hash": last_block.hash,
            "transactions": len(last_block.transactions)
        })

    async def broadcast(self, endpoint, data):
        for peer in self.peers:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(f"http://{peer}{endpoint}", json=data)
            except:
                self.peers.remove(peer)

    async def get_peers(self, request):
        return web.json_response(list(self.peers))

    async def add_peers(self, request):
        new_peers = await request.json()
        self.peers.update(new_peers)
        return web.json_response({"status": f"Added {len(new_peers)} peers"})

    async def start(self, host: str, port: int):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        print(f"🚀 Blockchain node running on {host}:{port}")
        await asyncio.Event().wait()

if __name__ == "__main__":
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    node = Node()
    asyncio.run(node.start(host, port))
