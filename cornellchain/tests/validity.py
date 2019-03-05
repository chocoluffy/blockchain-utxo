import unittest
import blockchain
import time
from blockchain.util import sha256_2_string
from blockchain.pow_block import PoWBlock
from blockchain.transaction import Transaction, TransactionOutput

class TestBlock(PoWBlock):
    """ We want to test PoW blocks without mining, so override seal check """

    def seal_is_valid(self):
        return True

    def calculate_appropriate_target(self):
        return int(2 ** 256)

class EvilBlock(TestBlock):
    """ Also override seal check so block always fails. """

    def seal_is_valid(self):
        return False

class BadTX(Transaction):
    """ Add evil invalid TXs that invalidate blocks. """

    def is_valid(self):
        return False

class ValidityTest(unittest.TestCase):

    def setUp(self):
        self.test_chain = blockchain.Blockchain()
        self.old_chain = blockchain.chain # PoW chains need to look up difficulty in the db, so shadow the global DB blockchain w our test chain
        blockchain.chain = self.test_chain

    def tearDown(self):
        blockchain.chain = self.old_chain # restore original chain

    def test_rejects_invalid_merkle(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .4), TransactionOutput("Alice", "Carol", .4)])

        # test an invalid merkle on genesis block is rejected, and valid merkle is accepted
        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.test_chain.add_block(block)
        old_merkle = block.merkle
        block.merkle = "fff"
        self.assertEqual(block.is_valid(), (False, "Merkle root failed to match"))
        block.merkle = old_merkle

        # test an invalid merkle on non-genesis block is rejected, and valid merkle is accepted
        block2 = TestBlock(1, [tx2], block.hash)
        self.assertTrue(block2.is_valid()[0])
        old_merkle = block2.merkle
        block2.merkle = "fff"
        self.assertEqual(block2.is_valid(), (False, "Merkle root failed to match"))
        block2.merkle = old_merkle
        self.assertTrue(block2.is_valid()[0])

    def test_rejects_invalid_hash(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .4), TransactionOutput("Alice", "Carol", .4)])

        # test an invalid hash on genesis block is rejected, and valid hash is accepted
        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.test_chain.add_block(block)
        old_hash = block.hash
        block.hash = "fff"
        self.assertEqual(block.is_valid(), (False, "Hash failed to match"))
        block.hash = old_hash

        # test an invalid hash on non-genesis block is rejected, and valid hash is accepted
        block2 = TestBlock(1, [tx2], block.hash)
        self.assertTrue(block2.is_valid()[0])
        old_hash = block2.hash
        block2.hash = "fff"
        self.assertEqual(block2.is_valid(), (False, "Hash failed to match"))
        block2.hash = old_hash
        self.assertTrue(block2.is_valid()[0])


    def test_rejects_too_many_txs(self):
        txs = []

        for i in range(901):
            txs.append(Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)]))

        # test too many txs in genesis
        block = TestBlock(0, txs, "genesis", is_genesis=True)
        self.assertEqual(block.is_valid(), (False, "Too many transactions"))

        # 900 txs should be fine
        block = TestBlock(0, txs[1:], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        # test too many txs outside genesis
        block = TestBlock(1, txs, block.hash)
        self.assertEqual(block.is_valid(), (False, "Too many transactions"))

    def test_invalid_genesis(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        # test bad height
        block.height = 1
        block.hash = block.calculate_hash() # recalculate hash to pash hash check
        self.assertEqual(block.is_valid(), (False, "Invalid genesis"))

        # test bad parent
        block.height = 0
        block.parent_hash = "invalid"
        block.hash = block.calculate_hash()
        self.assertEqual(block.is_valid(), (False, "Invalid genesis"))

    def test_nonexistent_parent(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertTrue(self.test_chain.add_block(block))
        inv_block = TestBlock(1, [], block.hash[:-1])
        self.assertEqual(inv_block.is_valid(), (False, "Nonexistent parent"))
        block = TestBlock(1, [], block.hash)
        self.assertTrue(block.is_valid()[0])

    def test_bad_height(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertTrue(self.test_chain.add_block(block))
        inv_block = TestBlock(2, [], block.hash)
        self.assertEqual(inv_block.is_valid(), (False, "Invalid height"))
        block = TestBlock(1, [], block.hash)
        self.assertTrue(block.is_valid()[0])

    def test_bad_timestamp(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertTrue(self.test_chain.add_block(block))
        inv_block = TestBlock(1, [], block.hash)
        inv_block.timestamp = block.timestamp - 1   # timestamp shouldn't be smaller than parent's
        inv_block.hash = inv_block.calculate_hash() # recalculate hash to pash hash check
        self.assertEqual(inv_block.is_valid(), (False, "Invalid timestamp"))
        block = TestBlock(1, [], block.hash)
        self.assertTrue(block.is_valid()[0])

    def test_bad_seal(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertTrue(self.test_chain.add_block(block))
        inv_block = EvilBlock(1, [], block.hash)
        self.assertEqual(inv_block.is_valid(), (False, "Invalid seal"))
        block = TestBlock(1, [], block.hash)
        self.assertTrue(block.is_valid()[0])

    def test_malformed_txs(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2_evil = BadTX([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .4), TransactionOutput("Alice", "Carol", .4)])
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .4), TransactionOutput("Alice", "Carol", .4)])

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2_evil], block.hash)
        self.assertEqual(block2.is_valid(), (False, "Malformed transaction included"))

        block2 = TestBlock(1, [tx2], block.hash)
        self.assertTrue(block2.is_valid()[0])

    def test_double_tx_inclusion_same_chain(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .4), TransactionOutput("Alice", "Carol", .4)])

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2], block.hash)
        self.assertTrue(block2.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block2))

        block3 = TestBlock(2, [tx2], block2.hash)
        self.assertEqual(block3.is_valid(), (False, "Double transaction inclusion"))

    def test_double_tx_inclusion_same_block(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .4), TransactionOutput("Alice", "Carol", .4)])

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2, tx2], block.hash)
        self.assertEqual(block2.is_valid(), (False, "Double transaction inclusion"))

    def test_failed_input_lookup(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2 = Transaction([tx1.hash + ":2"], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Carol", 1)]) # good tx id, bad input location
        tx3 = Transaction(["fakehash" + ":2"], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Carol", 1)]) # bad tx id
        # good txs
        tx4 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .2), TransactionOutput("Alice", "Carol", .2)])
        tx5 = Transaction([tx4.hash + ":0"], [TransactionOutput("Bob", "Bob", 0)])

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2], block.hash)
        self.assertEqual(block2.is_valid(), (False, "Required output not found"))

        block2 = TestBlock(1, [tx3], block.hash)
        self.assertEqual(block2.is_valid(), (False, "Required output not found"))

        block2 = TestBlock(1, [tx4, tx5], block.hash) # tx exists, but is in same block; this should work
        self.assertTrue(block2.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block2))

    def test_user_consistency(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Carol", "Bob", 0), TransactionOutput("Carol", "Carol", 0)]) # outputs created from wrong user (different than one that received inputs)
        tx3 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", 0), TransactionOutput("Carol", "Carol", 0)]) # two outputs from different users
        tx4 = Transaction([tx1.hash + ":0", tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", 0), TransactionOutput("Alice", "Carol", 0)]) # two inputs to different users
        tx5 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", 0), TransactionOutput("Alice", "Carol", 0)]) # this one is valid

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2], block.hash)
        self.assertEqual(block2.is_valid(), (False, "User inconsistencies"))

        block2 = TestBlock(1, [tx3], block.hash)
        self.assertEqual(block2.is_valid(), (False, "User inconsistencies"))

        block2 = TestBlock(1, [tx4], block.hash)
        self.assertEqual(block2.is_valid(), (False, "User inconsistencies"))

        block2 = TestBlock(1, [tx5], block.hash)
        self.assertTrue(block2.is_valid()[0])

    def test_doublespent_input_same_chain(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])

        # next two transactions spend same input twice (double spend)
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", 0), TransactionOutput("Alice", "Carol", 0)])
        tx3 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Carol", 0), TransactionOutput("Alice", "Carol", 0)])

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2], block.hash)
        self.assertTrue(block2.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block2))

        block3 = TestBlock(2, [tx3], block2.hash)
        self.assertEqual(block3.is_valid(), (False, "Double-spent input"))

        block3 = TestBlock(1, [tx3], block.hash)
        self.assertTrue(block3.is_valid()[0]) # doublespend should be allowed across forks

    def test_doublespent_input_same_block(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])

        # next two transactions spend same input twice (double spend)
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", 0), TransactionOutput("Alice", "Carol", 0)])
        tx3 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Carol", 0), TransactionOutput("Alice", "Carol", 0)])

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2, tx3], block.hash)
        self.assertEqual(block2.is_valid(), (False, "Double-spent input"))

    def test_input_txs_on_chain(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])

        # create chain of transactions; tx2 spends tx1, tx3 spends tx2
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .9), TransactionOutput("Alice", "Carol", 0)])
        tx3 = Transaction([tx2.hash + ":0"], [TransactionOutput("Bob", "Bob", .8)])

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2], block.hash)
        self.assertTrue(block2.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block2))

        block3 = TestBlock(1, [tx3], block.hash)
        self.assertEqual(block3.is_valid(), (False, "Input transaction not found"))

        block3 = TestBlock(2, [tx3], block2.hash)
        self.assertTrue(block3.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block3))

    def test_input_txs_in_block(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])

        # create chain of transactions; tx2 spends tx1, tx3 spends tx2
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .9), TransactionOutput("Alice", "Carol", 0)])
        tx3 = Transaction([tx2.hash + ":0"], [TransactionOutput("Bob", "Bob", .8)])

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2], block.hash)
        self.assertTrue(block2.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block2))

        block3 = TestBlock(1, [tx3], block.hash)
        self.assertEqual(block3.is_valid(), (False, "Input transaction not found"))

        block3 = TestBlock(1, [tx2, tx3], block.hash)
        self.assertTrue(block3.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block3))

    def test_no_money_creation(self):
        tx1 = Transaction([], [TransactionOutput("Alice", "Bob", 1), TransactionOutput("Alice", "Alice", 1)])
        tx2 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", 3), TransactionOutput("Alice", "Carol", 0)]) # single output creates money
        tx3 = Transaction([tx1.hash + ":1"], [TransactionOutput("Alice", "Bob", .9), TransactionOutput("Alice", "Carol", .9)]) # sum of outputs creates money

        block = TestBlock(0, [tx1], "genesis", is_genesis=True)
        self.assertTrue(block.is_valid()[0])
        self.assertTrue(self.test_chain.add_block(block))

        block2 = TestBlock(1, [tx2], block.hash)
        self.assertEqual(block2.is_valid(), (False, "Creating money"))

        block2 = TestBlock(1, [tx3], block.hash)
        self.assertEqual(block2.is_valid(), (False, "Creating money"))

if __name__ == '__main__':
    unittest.main()


