import asyncio
from libp2p import Host, PeerID
from libp2p.network.stream.net_stream_interface import INetStream
from libp2p.peer.peerinfo import info_from_p2p_addr

class P2PLayer:
    def __init__(self, host: Host):
        self.host = host
        self.peers = {}
        self.stream_handlers = {}

    async def connect(self, peer_addr: str):
        """Connect to peer with exponential backoff"""
        peer_info = info_from_p2p_addr(peer_addr)
        await self.host.connect(peer_info)

    async def broadcast(self, protocol: str, data: bytes):
        """Gossip protocol implementation"""
        for peer_id in self.peers:
            stream = await self.host.new_stream(peer_id, [protocol])
            await stream.write(data)

    async def handle_stream(self, stream: INetStream):
        """Async stream handler with rate limiting"""
        while True:
            data = await stream.read()
            await self.process_message(data)

class NetworkManager:
    """Orchestrates P2P connections and message routing"""
    def __init__(self, config):
        self.p2p = P2PLayer(config.host)
        self.msg_queue = asyncio.Queue()

    async def start(self):
        await self.p2p.start_listening()
        asyncio.create_task(self.process_messages())
