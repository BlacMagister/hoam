import argparse
import requests
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

class Wallet:
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256K1())
        self.public_key = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
    
    def sign(self, data: str) -> bytes:
        return self.private_key.sign(
            data.encode(),
            ec.ECDSA(hashes.SHA256())
        )

class BlockchainClient:
    def __init__(self, node_url):
        self.wallet = Wallet()
        self.node_url = node_url
        print(f"🔑 Wallet Address:\n{self.wallet.public_key}")

    def send(self, receiver: str, amount: float):
        tx_data = f"{self.wallet.public_key}{receiver}{amount}"
        signature = self.wallet.sign(tx_data)
        payload = {
            "sender": self.wallet.public_key,
            "receiver": receiver,
            "amount": amount,
            "signature": signature.hex()
        }
        try:
            res = requests.post(f"{self.node_url}/tx", json=payload)
            print(f"📤 Transaction Result: {res.json()}")
        except Exception as e:
            print(f"🔥 Error: {str(e)}")

    def mine(self):
        try:
            res = requests.post(f"{self.node_url}/mine", json={"miner": self.wallet.public_key})
            print(f"⛏️  Mining Result: {res.json()}")
        except Exception as e:
            print(f"🔥 Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🚀 Blockchain Client CLI")
    parser.add_argument('--node', default='http://localhost:8080', help="Node URL")
    parser.add_argument('--send', nargs=2, metavar=('RECEIVER', 'AMOUNT'))
    parser.add_argument('--mine', action='store_true')
    
    args = parser.parse_args()
    
    client = BlockchainClient(args.node)
    
    if args.send:
        client.send(args.send[0], float(args.send[1]))
    elif args.mine:
        client.mine()
    else:
        print("❌ No command provided. Use --help for options.")
