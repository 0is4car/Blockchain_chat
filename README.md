# README

inspired by https://github.com/dvf/blockchain, made changes according to our understanding and ideas. 

## Background

the non-repudiation comes with a reliable timestamp could be helpful in real life. For example, someone may come up with an amazaing research idea but doesn't have to realize it immediately, then they could publish this on the blockchain, no one could change either the timestamp or the idea itself. Another example is that if I borrow someone's car, I may want to upload the images on the blockchain so I could justify the condition before I use it.


## Design

There would be multiple nodes running as agents, providing APIs through HTTP and stores the whole blockchain. Client could log their messages to blockchain through peers, or run as a peer itself if it doesn't trust any peers.

Log a message on to blockchain is pretty much like git, client may first invoke `new_message` to append message(s) onto node's local memory as a list, then use `commit` to mine a block on blockchain and those messages are in the block. 

The time complxity of mining a block is about 100 times of sha256 calculation, given that only `proof` that makes the block's hash starts with `00` is considered valid.

As for consensus, the app simply queries chains stored at peers and use the longest one as the authoritative chain.

## Implementation

The `Blockchain` class basically includes:
- a list to store all blocks, 
- a list to stores peers' addresses. 


Two crucial attributes of Block class that make the blockchain are the hash of the previous block and a proof calculated by brute forcing the integer that holds sha256(previous_block.proof + this_block.proof + previous_block.hash).startswith('00'). 

## Requirement

The program is tested under Python 3.7.4 and Flask 1.1.1

## Usage

list of APIs:

- `/show_blockchain`: show current chain.

- `/sync`: syncronize the chain with peers and resolve conflicts.

- `/show_peers`: show all peers.

- `/add_peers`: add a peer.

- `/new_message`: add a new message to the local list, but not put it on blockchain.

- `/show_uncommitted_messages`: show all local messages ready for commit.

- `/commit`: put local messages on blockchain

### Run the program

`python blockchain.py localhost:5000`

### API example

#### using [HTTPie](https://github.com/jakubroztocil/httpie):

```
http http://localhost:8000/show_blockchain
http http://localhost:8000/new_message author=alice data=hello
http http://localhost:8000/show_uncommitted_messages
http http://localhost:8000/commit
http http://localhost:5000/add_peer 'peers:=["localhost:8000"]'
http http://localhost:5000/sync
```


