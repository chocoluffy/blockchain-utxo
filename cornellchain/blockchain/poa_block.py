
import blockchain
from blockchain.block import Block
import config
import binascii
import ecdsa
from ecdsa import SigningKey, VerifyingKey

class PoABlock(Block):
    """ Extends Block, adding proof-of-work primitives. """

    def seal_is_valid(self):
        """ Checks whether a block's seal_data forms a valid seal.
            In PoA, this means that Verif(PK, [block, sig]) = accept.
            (aka the unsealed block header is validly signed under the authority's public key)

            Returns:
                bool: True only if a block's seal data forms a valid seal according to PoA.
        """
        if self.seal_data == 0:
            return False

        # Decode signature to bytes, verify it
        signature = binascii.unhexlify(hex(self.seal_data)[2:].zfill(96))
        pk = VerifyingKey.from_string(self.get_public_key())
        try:
            return pk.verify(signature, self.unsealed_header().encode("utf-8"))
        except ecdsa.keys.BadSignatureError:
            return False

    def get_weight(self):
        """ Gets the approximate total amount of work that has gone into making a block.
            The consensus weight of a block is how much harder a block is to mine
            than the easiest possible block, which for PoA is always 1.

        Returns:
            int: The consensus weight of a block.
        """
        return 1

    def mine(self):
        """ PoA signer; seals a block with new seal data by signing it, checking that
            signature is valid, and returning.
        """

        # Use NIST192p curve and ECDSA, encoding block header as UTF-8
        # use self.get_private_key() for key
        # encode result as int and set using set_seal_data
        # make sure to check that output is valid seal with provided code
        # (if seal is invalid, repeat)

        # Placeholder for (1b)
        signed_key = SigningKey.from_string(self.get_private_key())
        new_seal_data = signed_key.sign(self.unsealed_header().encode("utf8"))
        while not self.seal_is_valid():
            self.set_seal_data((int.from_bytes(new_seal_data, byteorder='big')))


    def calculate_appropriate_target(self):
        """ Target in PoA is currently meaningless """
        return 0

    def get_public_key(self):
        """ Returns public key of PoA authority. """
        return binascii.unhexlify(config.AUTHORITY_PK)

    def get_private_key(self):
        """ Returns private key of PoA authority. """
        return binascii.unhexlify(config.AUTHORITY_SK)

