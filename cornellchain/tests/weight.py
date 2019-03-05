import unittest
from blockchain.util import sha256_2_string
from blockchain.pow_block import PoWBlock
from blockchain.transaction import Transaction, TransactionOutput

class TestBlock(PoWBlock):
    """ We are testing block weight, so allow for custom targets """

    def set_target(self, target):
        self.target = target

class WeightTest(unittest.TestCase):

    def test_pow_weights(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertEqual(block.get_weight(), 256)
        block.set_target(0)
        self.assertEqual(block.get_weight(), 115792089237316195423570985008687907853269984665640564039457584007913129639936)
        block.set_target(5)
        self.assertEqual(block.get_weight(), 23158417847463240370264632408929802004223670806058194825653911827816894169088)
        block.set_target(100)
        self.assertEqual(block.get_weight(), 1157920892373161978339780513971733211662131231773844678227620746821023825920)
        block.set_target(2 ** 254)
        self.assertEqual(block.get_weight(), 4)
        block.set_target(2 ** 257)
        self.assertEqual(block.get_weight(), 0)

if __name__ == '__main__':
    unittest.main()


