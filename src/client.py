import requests
import time

NODE_URL = "http://localhost:5000"

def simulate_mining():
    while True:
        try:
            response = requests.post(f"{NODE_URL}/mine", json={"data": "Block data"})
            if response.status_code == 200:
                block = response.json()['block']
                print(f"Mined block #{block['index']} | Hash: {block['hash']}")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(5)  # Mining setiap 5 detik

if __name__ == '__main__':
    print("🚀 Starting mock miner...")
    simulate_mining()
