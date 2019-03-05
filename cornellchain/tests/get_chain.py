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

class GetChainTest(unittest.TestCase):

    def setUp(self):
        self.test_chain = blockchain.Blockchain()
        self.old_chain = blockchain.chain # PoW chains need to look up difficulty in the db, so shadow the global DB blockchain w our test chain
        blockchain.chain = self.test_chain

    def tearDown(self):
        blockchain.chain = self.old_chain # restore original chain

    def test_pow_get_chain_emptychain(self):
        self.assertEqual(self.test_chain.get_chain_ending_with("test"), [])

    def test_pow_get_chain_genesisonly(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertTrue(self.test_chain.add_block(block))
        self.assertEqual(self.test_chain.get_chain_ending_with("test"), [])
        self.assertEqual(self.test_chain.get_chain_ending_with(block.hash), [block.hash])

    def test_pow_get_chain_linear_chain(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertTrue(self.test_chain.add_block(block))
        block2 = TestBlock(1, [], block.hash)
        self.assertTrue(self.test_chain.add_block(block2))
        block3 = TestBlock(2, [], block2.hash)
        self.assertTrue(self.test_chain.add_block(block3))
        block4 = TestBlock(3, [], block3.hash)
        self.assertTrue(self.test_chain.add_block(block4))
        self.assertEqual(self.test_chain.get_chain_ending_with(block.hash), [block.hash])
        self.assertEqual(self.test_chain.get_chain_ending_with(block2.hash), [block2.hash, block.hash])
        self.assertEqual(self.test_chain.get_chain_ending_with(block3.hash), [block3.hash, block2.hash, block.hash])
        self.assertEqual(self.test_chain.get_chain_ending_with(block4.hash), [block4.hash, block3.hash, block2.hash, block.hash])


    def test_pow_get_chain_with_forks(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertTrue(self.test_chain.add_block(block))
        block2 = TestBlock(1, [], block.hash)
        self.assertTrue(self.test_chain.add_block(block2))
        block3 = TestBlock(1, [], block.hash)
        block3.set_seal_data(5) # change seal data to enforce that block2, block3 differ
        self.assertTrue(self.test_chain.add_block(block3))
        block4 = TestBlock(2, [], block2.hash)
        self.assertTrue(self.test_chain.add_block(block4))
        self.assertEqual(self.test_chain.get_chain_ending_with(block.hash), [block.hash])
        self.assertEqual(self.test_chain.get_chain_ending_with(block2.hash), [block2.hash, block.hash])
        self.assertEqual(self.test_chain.get_chain_ending_with(block3.hash), [block3.hash, block.hash])
        self.assertEqual(self.test_chain.get_chain_ending_with(block4.hash), [block4.hash, block2.hash, block.hash])


if __name__ == '__main__':
    unittest.main()


