from blockchain.pow_block import PoWBlock

class TestBlock(PoWBlock):
    """ A test block is just a PoW block that is always valid;
        use if you need to to test e.g. block validity features.
    """

    def is_valid(self):
        return True, "TEST BLOCK"

