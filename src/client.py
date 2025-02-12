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

class BlockchainCLI:
    def __init__(self):
        self.wallet = Wallet()
        self.node_url = "http://localhost:8080"
        print(f"💰 Wallet created | Address: {self.wallet.public_key[:50]}...")

    def send_transaction(self, receiver: str, amount: float):
        tx_data = f"{self.wallet.public_key}{receiver}{amount}"
        signature = self.wallet.sign(tx_data)
        tx = {
            "sender": self.wallet.public_key,
            "receiver": receiver,
            "amount": amount,
            "signature": signature.hex()
        }
        try:
            response = requests.post(f"{self.node_url}/tx", json=tx)
            print(f"📤 Transaction Status: {response.json()}")
        except requests.ConnectionError:
            print("🔌 Error: Could not connect to node")

    def mine_block(self):
        try:
            response = requests.post(f"{self.node_url}/mine")
            print(f"⛏️  Mining Result: {response.json()}")
        except requests.ConnectionError:
            print("🔌 Error: Could not connect to node")

    def start(self):
        parser = argparse.ArgumentParser(description="🚀 Future Blockchain CLI")
        parser.add_argument('--send', nargs=2, metavar=('RECEIVER', 'AMOUNT'))
        parser.add_argument('--mine', action='store_true')
        
        args = parser.parse_args()
        
        if args.send:
            receiver, amount = args.send
            self.send_transaction(receiver, float(amount))
        elif args.mine:
            self.mine_block()
        else:
            print("❌ No command provided. Use --help for options.")

if __name__ == "__main__":
    BlockchainCLI().start()
