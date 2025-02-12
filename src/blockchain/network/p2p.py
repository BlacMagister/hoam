import asyncio
from libp2p import new_node
from libp2p.peer.peerinfo import info_from_p2p_addr
from libp2p.crypto.secp256k1 import Secp256k1PrivateKey
import multiaddr
import msgpack

class P2PService:
    def __init__(self, config: Dict):
        self.node = None
        self.config = config
        self.peers = set()
        self.message_queue = asyncio.Queue()
        self.private_key = Secp256k1PrivateKey.generate()

    async def start(self):
        self.node = await new_node(
            key=self.private_key,
            listen_addrs=[multiaddr.Multiaddr(self.config['listen_addr'])]
        )
        
        self.node.set_stream_handler(
            self.config['protocol_id'], 
            self._handle_stream
        )
        
        print(f"🌐 P2P Node ID: {self.node.get_id()} | Listening on: {self.config['listen_addr']}")
        await self._connect_bootstrap_nodes()

    async def _connect_bootstrap_nodes(self):
        for addr in self.config['bootstrap_nodes']:
            try:
                maddr = multiaddr.Multiaddr(addr)
                peer_info = info_from_p2p_addr(maddr)
                await self.node.connect(peer_info)
                self.peers.add(peer_info.peer_id)
            except Exception as e:
                print(f"⚠️ Failed to connect to bootstrap node {addr}: {str(e)}")

    async def _handle_stream(self, stream):
        try:
            data = await stream.read()
            decoded = msgpack.unpackb(data)
            await self.message_queue.put({
                'peer': stream.peer_id,
                'data': decoded
            })
        finally:
            await stream.close()

    async def broadcast(self, message: Dict):
        msg = msgpack.packb(message)
        for peer in self.peers:
            try:
                stream = await self.node.dial_peer(peer, [self.config['protocol_id']])
                await stream.write(msg)
            except Exception as e:
                print(f"🚫 Failed to send to {peer}: {str(e)}")
                self.peers.remove(peer)

    async def periodic_discovery(self):
        while True:
            await self._perform_discovery()
            await asyncio.sleep(self.config['discovery_interval'])

    async def _perform_discovery(self):
        for peer in list(self.node.peerstore.peers()):
            if peer not in self.peers:
                try:
                    await self.node.connect(peer)
                    self.peers.add(peer)
                except:
                    continue
