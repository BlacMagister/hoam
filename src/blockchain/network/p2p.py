import asyncio
from libp2p import new_node
from libp2p.peer.peerinfo import info_from_p2p_addr
from multiaddr import Multiaddr
import json

class P2PNetwork:
    def __init__(self, config: dict):
        self.node = None
        self.config = config
        self.peers = set()

    async def start(self):
        self.node = await new_node(
            key_type="secp256k1",
            listen_addrs=[Multiaddr(self.config['listen_addr'])]
        )
        await self.bootstrap()
        asyncio.create_task(self.listen_for_peers())

    async def bootstrap(self):
        for addr in self.config['bootstrap_nodes']:
            try:
                maddr = Multiaddr(addr)
                peer_info = info_from_p2p_addr(maddr)
                await self.node.connect(peer_info)
                self.peers.add(peer_info.peer_id)
            except Exception as e:
                print(f"Connection failed to {addr}: {str(e)}")

    async def broadcast(self, message_type: str, data: dict):
        message = {'type': message_type, 'data': data}
        for peer_id in self.peers:
            stream = await self.node.dial_peer(peer_id, self.config['protocols'])
            await stream.write(json.dumps(message).encode())

    async def listen_for_peers(self):
        async for connection in self.node.connections():
            self.peers.add(connection.peer_id)
