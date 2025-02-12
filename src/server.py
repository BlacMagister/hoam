from aiohttp import web
import aiohttp
import asyncio
from blockchain import Blockchain, Transaction
from cryptography.hazmat.primitives import serialization

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
        chain_data = []
        for block in self.blockchain.chain:
            block_data = {
                "hash": block.hash,
                "header": {
                    "version": block.header.version,
                    "previous_hash": block.header.previous_hash,
                    "merkle_root": block.header.merkle_root,
                    "timestamp": block.header.timestamp,
                    "difficulty": block.header.difficulty,
                    "nonce": block.header.nonce
                },
                "transactions": [
                    {
                        "sender": tx.sender,
                        "receiver": tx.receiver,
                        "amount": tx.amount,
                        "signature": tx.signature.hex()
                    } for tx in block.transactions
                ]
            }
            chain_data.append(block_data)
        return web.json_response(chain_data)

    async def new_transaction(self, request):
        data = await request.json()
        try:
            tx = Transaction(
                data['sender'],
                data['receiver'],
                data['amount'],
                bytes.fromhex(data['signature'])
            )
            if self.blockchain.add_transaction(tx):
                await self.broadcast_tx(tx)
                return web.json_response({"status": "Transaction added to mempool"})
            return web.json_response({"status": "Invalid transaction"}, status=400)
        except KeyError:
            return web.json_response({"error": "Invalid transaction format"}, status=400)

    async def new_block(self, request):
        data = await request.json()
        return web.Response(text="Block endpoint")

    async def broadcast_tx(self, tx):
        for peer in self.peers:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        f"http://{peer}/tx",
                        json={
                            "sender": tx.sender,
                            "receiver": tx.receiver,
                            "amount": tx.amount,
                            "signature": tx.signature.hex()
                        }
                    )
            except:
                self.peers.remove(peer)

    async def get_peers(self, request):
        return web.json_response(list(self.peers))

    async def add_peers(self, request):
        new_peers = await request.json()
        self.peers.update(new_peers)
        return web.json_response({"status": "Peers updated"})

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        print("🛸 Node running on http://0.0.0.0:8080")
        await asyncio.Event().wait()

if __name__ == "__main__":
    node = Node()
    asyncio.run(node.start())
