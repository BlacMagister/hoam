import argparse
import requests
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

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

    def send_transaction(self, receiver: str, amount: float):
        tx_data = f"{self.wallet.public_key}{receiver}{amount}"
        signature = self.wallet.sign(tx_data)
        tx = {
            "sender": self.wallet.public_key,
            "receiver": receiver,
            "amount": amount,
            "signature": signature.hex()
        }
        response = requests.post(f"{self.node_url}/tx", json=tx)
        print(response.json())

    def mine(self):
        response = requests.post(f"{self.node_url}/mine", json={
            "miner": self.wallet.public_key
        })
        print(f"Mined Block: {response.json()}")

    def start(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--send', nargs=2)
        parser.add_argument('--mine', action='store_true')
        args = parser.parse_args()

        if args.send:
            self.send_transaction(args.send[0], float(args.send[1]))
        elif args.mine:
            self.mine()

if __name__ == "__main__":
    BlockchainCLI().start()
