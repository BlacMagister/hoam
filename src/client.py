import requests
import time

SERVER_URL = "http://localhost:5000"

def mine_forever():
    while True:
        try:
            response = requests.post(f"{SERVER_URL}/mine", json={"data": "New Block"})
            if response.status_code == 200:
                block = response.json()
                print(f"Mined Block #{block['index']}")
                print(f"Hash: {block['hash']}")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(10)

if __name__ == '__main__':
    mine_forever()
