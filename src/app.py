from flask import Flask, jsonify, request
from blockchain import Blockchain
import time

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify([block.to_dict() for block in blockchain.chain]), 200

@app.route('/mine', methods=['POST'])
def mine_block():
    data = request.json.get('data', 'Mined Block')
    new_block = blockchain.add_block(data)
    response = {
        "message": "Block mined!",
        "block": new_block.to_dict()
    }
    return jsonify(response), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "chain_length": len(blockchain.chain),
        "difficulty": blockchain.difficulty,
        "valid": blockchain.is_valid()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
