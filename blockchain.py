import sys
import json
import time
import requests
from flask import Flask, request, jsonify
from dataclasses import dataclass
from hashlib import sha256

@dataclass
class Block:
    id : int
    messages : list
    timestamp : int
    previous_hash : str
    proof : int

    @property
    def hash(self):
        serilized = json.dumps(self.__dict__, sort_keys=True)
        return sha256(serilized.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.uncommitted_messages = []
        self.peers = set()
        gensis_block = Block(0, [], time.time(), '0', 0)
        self.chain.append(gensis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def last_index(self):
        return len(self.chain)-1

    @staticmethod
    def validate_proof(last_proof, proof, last_hash):
        hash = sha256(f'{last_proof}{proof}{last_hash}'.encode()).hexdigest()
        return hash.startswith('00')

    def validate_chain(self,chain):
        chain = [Block(**block_dict) for block_dict in chain]
        for b1, b2 in zip(chain[:-1], chain[1:]):
            if not b2.previous_hash == b1.hash:
                return False
            if not self.validate_proof(b1.proof, b2.proof, b1.hash):
                return False

        return True


    def calculate_proof(self, block):
        while not self.validate_proof(self.last_block.proof,
                block.proof, self.last_block.hash):
            block.proof += 1
        return block.proof

    def commit(self):
        if not self.uncommitted_messages:
            return False
        last_block = self.last_block
        new_block = Block(self.last_index+1, self.uncommitted_messages,
                time.time(), last_block.hash, 0)
        self.calculate_proof(new_block)
        self.chain.append(new_block)
        self.uncommitted_messages = []
        return True

    def new_message(self, message):
        if not message:
            return False
        self.uncommitted_messages.append(message)
        return len(self.uncommitted_messages)

    def add_peer(self, address):
        self.peers.add(address)
        return True

    def sync(self):
        if not self.peers:
            return False
        m = len(self.chain)
        chain = self.chain
        for node in self.peers:
            resp = requests.get(f'http://{node}/show_blockchain')
            if resp.status_code == 200:
                data = resp.json()
                print(data['chain'])
                if int(data['length']) > m and blockchain.validate_chain(data['chain']):
                    m = int(data['length'])
                    chain = data['chain']
        if chain != self.chain:
            self.chain = chain
            return True

        return False
                    
                


####################################
# API
####################################
app = Flask(__name__)

@app.route('/show_blockchain', methods=['GET'])
def show_blockchain():
    chain = [block.__dict__ for block in blockchain.chain]
    res = {'length': len(blockchain.chain), 'chain': chain}
    return jsonify(res), 200

@app.route('/get_chainlength', methods=['GET'])
def get_chainlength():
    return str(len(blockchain.chain)), 200

@app.route('/sync', methods=['GET'])
def sync():
    updated = blockchain.sync()
    return str(updated), 200

@app.route('/show_peers', methods=['GET'])
def show_peers():
    return jsonify(list(blockchain.peers)), 200

@app.route('/add_peer', methods=['POST'])
def add_peer():
    print(request.get_json())
    peers = request.get_json().get('peers')
    res = []
    for peer in peers:
        try:
            blockchain.add_peer(peer)
            res.append(peer)
        except:
            pass
    return jsonify(res), 200

@app.route('/new_message', methods=['POST'])
def new_message():
    try:
        data = json.loads(request.data)
        author = data.get('author')
        message = data.get('message')
        return str(blockchain.new_message({
            'author':author, 
            'message':message})), 200

    except:
        return 'author and message are required', 400

@app.route('/show_uncommitted_messages', methods=['GET'])
def show_uncommitted_messages():
    return jsonify(blockchain.uncommitted_messages), 200

@app.route('/commit', methods=['GET'])
def commit():
    return str(blockchain.commit()), 200

blockchain = Blockchain()
try:
    mynode = sys.argv[1]
except:
    print(f'usage: python {__file__} ip:port')
    sys.exit()

app.run(debug=True, port=int(mynode.split(':')[1]))
