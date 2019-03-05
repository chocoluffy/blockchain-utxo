import unittest
from blockchain.util import sha256_2_string
from blockchain.poa_block import PoABlock
from blockchain.transaction import Transaction, TransactionOutput

class TestBlock(PoABlock):
    """ We are testing signatures, so allow for direct seal modification """

    def force_set_seal_data(self, seal_data):
        self.seal_data = seal_data


class PoATest(unittest.TestCase):

    def test_poa_mining(self):
        block = TestBlock(0, [], "genesis", is_genesis=True)
        self.assertFalse(block.seal_is_valid()) # seal is initially invalid (no seal data)
        block.mine()
        self.assertTrue(block.seal_is_valid()) # after adding seal data, seal is valid
        self.assertTrue(type(block.seal_data) == int) # make sure seal is right type
        block.force_set_seal_data(block.seal_data - 1)
        self.assertFalse(block.seal_is_valid()) # make sure invalid seals don't pass validation
        block.force_set_seal_data(0)
        self.assertFalse(block.seal_is_valid())

if __name__ == '__main__':
    unittest.main()


