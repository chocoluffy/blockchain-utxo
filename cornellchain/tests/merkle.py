import unittest
from blockchain.pow_block import PoWBlock
from blockchain.transaction import Transaction, TransactionOutput

class TestBlock(PoWBlock):
    """ We are testing blockhashing; make sure timestamp is consistent. """

    def set_dummy_timestamp(self):
        self.timestamp = ""

class MerkleRootTest(unittest.TestCase):

    def test_merkle_root(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 3)])
        tx2 = Transaction([tx1.hash + ":0"], [TransactionOutput("Alice", "Bob", 2), TransactionOutput("Alice", "Carol", 1)])
        tx3 = Transaction([tx2.hash + ":0"], [TransactionOutput("Bob", "Carol", 1), TransactionOutput("Bob", "Bob", 1)])
        tx4 = Transaction([tx3.hash + ":0"], [TransactionOutput("Carol", "Alice", 0.5), TransactionOutput("Carol", "Carol", 0.5)])

        block1 = TestBlock(0, [tx1], "genesis", is_genesis=True)
        block2 = TestBlock(0, [tx1,tx2], "genesis", is_genesis=True)
        block3 = TestBlock(0, [tx1, tx2, tx3, tx4], "genesis", is_genesis=True)

        for block in [block1, block2, block3]:
            block.set_dummy_timestamp()

        self.assertEqual(block1.merkle, "70dd3a969ee311d9749d8f1c2f03ab1dc4930ca0be58d231a73dfeeb85f5b68d")
        self.assertEqual(block2.merkle, "e0559c662f64c8fd1b638384ecbb1104335445a07114fd7d197316402e2f6f4c")
        self.assertEqual(block3.merkle, "039eceb401b485400f19bca99158b9dd2fcd13e9e4f287fde16f81fa58074a51")

if __name__ == '__main__':
    unittest.main()
