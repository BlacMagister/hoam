from flask import Flask, jsonify, request
from blockchain import Blockchain
import time

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [{
        "index": block.index,
        "timestamp": block.timestamp,
        "data": block.data,
        "hash": block.hash,
        "previous_hash": block.previous_hash
    } for block in blockchain.chain]
    return jsonify(chain_data)

@app.route('/mine', methods=['POST'])
def mine_block():
    data = request.json.get('data', 'Mined Block')
    new_block = blockchain.add_block(data)
    response = {
        "index": new_block.index,
        "hash": new_block.hash,
        "previous_hash": new_block.previous_hash
    }
    return jsonify(response)

@app.route('/validate', methods=['GET'])
def validate_chain():
    is_valid = blockchain.validate()
    return jsonify({"valid": is_valid})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
