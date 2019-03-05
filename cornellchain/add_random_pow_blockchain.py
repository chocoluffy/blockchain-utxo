import blockchain
from blockchain.transaction import Transaction, TransactionOutput
from blockchain.pow_block import PoWBlock
import transaction
import random
import config

if len(blockchain.chain.chain) > 0:
    print("Blockchain already populated!  Remove files in " + config.DB_PATH + " to re-generate a new chain.")
    exit(1)

USERS = ["Alice", "Bob", "Charlie", "Dave", "Errol", "Frank"]
HEIGHT_TO_REACH = 100
MAX_TXS_PER_BLOCK = 50
FORK_PROBABILITY = .3

# basic wallet functionality; track UTXOs for users
user_utxos = {}
for user in USERS:
    user_utxos[user] = []

# insert genesis block; populate all users w huge balance
outputs = []
for user in USERS:
    genesis_utxo = TransactionOutput("Genesis", user, 100000000)
    outputs.append(genesis_utxo)
genesis_tx = Transaction([], outputs)
for user_num in range(len(USERS)):
    user = USERS[user_num]
    user_utxos[user].append((genesis_tx.hash + ":" + str(user_num), 100000000))
genesis_block = PoWBlock(0, [genesis_tx], "genesis", is_genesis=True)
blockchain.chain.add_block(genesis_block)

curr_height = 1
parent = genesis_block


while curr_height <= HEIGHT_TO_REACH:
    chain = blockchain.chain
    txs = []
    if random.random() < FORK_PROBABILITY:
        if parent.parent_hash == "genesis":
            continue
        curr_height -= 1
        new_parent_hash = random.choice(chain.chain[curr_height - 1]) # fork random previous block
        parent = chain.blocks[new_parent_hash]

    eligible_parents = [chain.blocks[block_hash] for block_hash in chain.get_chain_ending_with(parent.hash)]
    eligible_txs = []
    for parent_candidate in eligible_parents:
        eligible_txs += [tx.hash for tx in parent_candidate.transactions]

    num_txs = int(random.random() * MAX_TXS_PER_BLOCK)
    if curr_height < 10:
        num_txs += 5 # seed early blocks with lots of txs to prevent duplicate hashes
    for i in range(num_txs):
        # choose a random sender and receiver
        sender = random.choice(USERS)
        receiver = random.choice(USERS)
        if len(user_utxos[sender]) == 0:
            continue
        parent_utxo = random.choice(user_utxos[sender])
        tries = 0
        while not parent_utxo[0].split(":")[0] in eligible_txs:
            parent_utxo = random.choice(user_utxos[sender])
            tries += 1
            if tries > 200000:
                break
        if tries > 200000:
            break
        user_utxos[sender].remove(parent_utxo)
        amount_to_send = int(parent_utxo[1] * random.random())
        change_amount = parent_utxo[1] - amount_to_send
        sending_utxo = TransactionOutput(sender, receiver, amount_to_send)
        change_utxo = TransactionOutput(sender, sender, change_amount)
        tx = Transaction([parent_utxo[0]], [sending_utxo, change_utxo])
        txs.append(tx)
        eligible_txs.append(tx.hash)
        user_utxos[receiver].append((tx.hash + ":0", amount_to_send))
        user_utxos[sender].append((tx.hash + ":1", change_amount))

    block = PoWBlock(curr_height, txs, parent.hash)
    block.mine()
    out_status = chain.add_block(block)
    if not out_status:
        # block add failed; try again
        continue
    print("Added block at height", curr_height)
    curr_height += 1
    parent = block
