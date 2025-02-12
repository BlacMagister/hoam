from libp2p import new_node
from libp2p.peer.peerinfo import info_from_p2p_addr
import multiaddr
import asyncio

class P2PNetwork:
    def __init__(self, config: dict):
        self.node = None
        self.config = config
        self.protocols = {}
    
    async def start(self):
        self.node = await new_node(
            key_type="secp256k1",
            listen_addrs=[multiaddr.Multiaddr(self.config['listen_addr'])]
        )
        
        for proto in self.config['protocols']:
            self.node.set_stream_handler(proto, self.handle_stream)
        
        print(f"🏁 P2P node running at {self.node.get_addrs()[0]}")
    
    async def connect(self, peer_addr: str):
        addr = multiaddr.Multiaddr(peer_addr)
        peer_info = info_from_p2p_addr(addr)
        await self.node.connect(peer_info)
    
    async def handle_stream(self, stream):
        data = await stream.read()
        # Process incoming network messages
        await self.route_message(data)
    
    async def broadcast(self, message: dict):
        for peer in self.node.peerstore.peers():
            stream = await self.node.dial_peer(peer, self.config['protocols'])
            await stream.write(json.dumps(message).encode())
