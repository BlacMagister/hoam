from aiohttp import web
import aiohttp
import json
import asyncio
from blockchain import Blockchain, Transaction

class Node:
    def __init__(self):
        self.app = web.Application()
        self.blockchain = Blockchain()
        self.peers = set()
        self.app.add_routes([
            web.get('/chain', self.get_chain),
            web.post('/tx', self.new_transaction),
            web.post('/block', self.new_block),
            web.get('/peers', self.get_peers),
            web.post('/peers', self.add_peers)
        ])

    async def get_chain(self, request):
        return web.json_response([{
            "hash": block.hash,
            "header": block.header.__dict__,
            "transactions": [tx.__dict__ for tx in block.transactions]
        } for block in self.blockchain.chain])

    async def new_transaction(self, request):
        data = await request.json()
        tx = Transaction(
            data['sender'],
            data['receiver'],
            data['amount'],
            bytes.fromhex(data['signature'])
        if self.blockchain.add_transaction(tx):
            await self.broadcast_tx(tx)
            return web.json_response({"status": "success"})
        return web.json_response({"status": "invalid"}, status=400)

    async def new_block(self, request):
        data = await request.json()
        # Implement block validation and consensus logic
        return web.Response()

    async def broadcast_tx(self, tx):
        for peer in self.peers:
            async with aiohttp.ClientSession() as session:
                await session.post(f"http://{peer}/tx", json={
                    "sender": tx.sender,
                    "receiver": tx.receiver,
                    "amount": tx.amount,
                    "signature": tx.signature.hex()
                })

    async def get_peers(self, request):
        return web.json_response(list(self.peers))

    async def add_peers(self, request):
        peers = await request.json()
        self.peers.update(peers)
        return web.json_response({"status": "added"})

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        print("Node running on port 8080")
        await asyncio.Event().wait()

if __name__ == "__main__":
    node = Node()
    asyncio.run(node.start())
