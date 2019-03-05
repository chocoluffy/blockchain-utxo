import unittest
from blockchain.util import sha256_2_string
from blockchain.pow_block import PoWBlock
from blockchain.transaction import Transaction, TransactionOutput

class TestBlock(PoWBlock):
    """ We are testing blockhashing; make sure timestamp is consistent. """

    def set_dummy_timestamp(self):
        self.timestamp = ""

class HashTest(unittest.TestCase):

    def test_double_sha256(self):
        self.assertEqual(sha256_2_string("Data test"), "95cb8ec3a627b3b25902c7d38ca7e51a3d54ad99df0302e93e899337b8e73b2e")
        self.assertEqual(sha256_2_string("Data test 2"), "bd069191dbc430b9627617c4480a5ec6d25106ad278de785509510ab2f5b2eff")
        self.assertEqual(sha256_2_string("whee"), "53447992e1eea5d4dea2d74ce6e4e911022c7222d07246c1ff9a47f83853ad6a")
        self.assertEqual(sha256_2_string(""), "5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456")

    def test_blockchain_hash(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2 = Transaction([tx1.hash + ":0"], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Carol", 1)])
        block = TestBlock(0, [tx1,tx2], "genesis", is_genesis=True)
        block.set_dummy_timestamp()
        self.assertEqual(sha256_2_string(block.header()), "9fc4ae4f2e6a68a0e79a57c4491b03a72f9a4bcdbc6ab7213e0f9334d800c57d")

if __name__ == '__main__':
    unittest.main()


