import unittest
from tests.hash import HashTest
from tests.weight import WeightTest
from tests.get_chain import GetChainTest
from tests.validity import ValidityTest
from tests.poa import PoATest
from tests.merkle import MerkleRootTest

# Test for (1a) - sha256_2_string
suite = unittest.TestLoader().loadTestsFromTestCase(HashTest)
unittest.TextTestRunner(verbosity=2).run(suite)

# Test for (1a) - get_weight
suite = unittest.TestLoader().loadTestsFromTestCase(WeightTest)
unittest.TextTestRunner(verbosity=2).run(suite)

# Test for (1a) - get_chain_ending_with
suite = unittest.TestLoader().loadTestsFromTestCase(GetChainTest)
unittest.TextTestRunner(verbosity=2).run(suite)

# Test for (1a) - is_valid
suite = unittest.TestLoader().loadTestsFromTestCase(ValidityTest)
unittest.TextTestRunner(verbosity=2).run(suite)

# Test for (1b) - mine
suite = unittest.TestLoader().loadTestsFromTestCase(PoATest)
unittest.TextTestRunner(verbosity=2).run(suite)

# Test for (1c) - calculate_merkle_root
suite = unittest.TestLoader().loadTestsFromTestCase(MerkleRootTest)
unittest.TextTestRunner(verbosity=2).run(suite)
