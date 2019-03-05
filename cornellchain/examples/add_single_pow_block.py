import blockchain
from blockchain.transaction import Transaction, TransactionOutput
from blockchain.pow_block import PoWBlock
import transaction

# create some transactions
tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
tx2 = Transaction([tx1.hash + ":0"], [TransactionOutput("Alice", "Bob", .4), TransactionOutput("Alice", "Carol", .4)])

# create an unsealed block
block = PoWBlock(0, [tx1,tx2], "genesis", is_genesis=True)

# run the mining loop until a valid PoW seal is created (final hash should have 2 leading 0s)
block.mine()

# add the block to the blockchain
assert(blockchain.chain.add_block(block))

# display the block
print(block.header())
print(block.hash)
