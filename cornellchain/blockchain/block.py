from abc import ABC, abstractmethod # We want to make Block an abstract class; either a PoW or PoA block
import blockchain
from blockchain.util import sha256_2_string, encode_as_str
import time
import persistent
from blockchain.util import nonempty_intersection

class Block(ABC, persistent.Persistent):

    def __init__(self, height, transactions, parent_hash, is_genesis=False):
        """ Creates a block template (unsealed).

        Args:
            height (int): height of the block in the chain (# of blocks between block and genesis).
            transactions (:obj:`list` of :obj:`Transaction`): ordered list of transactions in the block.
            parent_hash (str): the hash of the parent block in the blockchain.
            is_genesis (bool, optional): True only if the block is a genesis block.

        Attributes:
            parent_hash (str): the hash of the parent block in blockchain.
            height (int): height of the block in the chain (# of blocks between block and genesis).
            transactions (:obj:`list` of :obj:`Transaction`): ordered list of transactions in the block.
            timestamp (int): Unix timestamp of the block
            target (int): Target value for the block's seal to be valid (different for each seal mechanism)
            is_genesis (bool): True only if the block is a genesis block (first block in the chain).
            merkle (str): Merkle hash of the list of transactions in a block, uniquely identifying the list.
            seal_data (int): Seal data for block (in PoW this is the nonce satisfying the PoW puzzle; in PoA, the signature of the authority"
            hash (str): Hex-encoded SHA256^2 hash of the block header (self.header())
        """
        self.parent_hash = parent_hash
        self.height = height
        self.transactions = transactions
        self.timestamp = int(time.time())
        self.target = self.calculate_appropriate_target()
        self.is_genesis = is_genesis
        self.merkle = self.calculate_merkle_root()
        self.seal_data = 0 # temporarily set seal_data to 0
        self.hash = self.calculate_hash() # keep track of hash for caching purposes

    def calculate_merkle_root(self):
        """ Gets the Merkle root hash for a given list of transactions.

        This method is incomplete!  Right now, it only hashes the
        transactions together, which does not enable the same type
        of lite client support a true Merkle hash would.

        Returns:
            str: Merkle hash of the list of transactions in a block, uniquely identifying the list.
        """
        # Placeholder for (1c)
        all_hashes = [sha256_2_string(str(tx)) for tx in self.transactions]

        if len(all_hashes) == 0:
            return ""
        
        new_lst = all_hashes
        while len(new_lst) > 1:
            next_lst = []
            if len(new_lst) % 2 == 0: # even
                for i in range(0, len(new_lst), 2):
                    next_lst.append(sha256_2_string("".join([new_lst[i], new_lst[i+1]])))
            elif len(new_lst) % 2 != 0: # odd
                for i in range(0, len(new_lst) - 1, 2):
                    next_lst.append(sha256_2_string("".join([new_lst[i], new_lst[i+1]])))
                next_lst.append(sha256_2_string("".join([new_lst[-1], new_lst[-1]])))
            new_lst = next_lst
        return new_lst[0]


    def unsealed_header(self):
        """ Computes the header string of a block (the component that is sealed by mining).

        Returns:
            str: String representation of the block header without the seal.
        """
        return encode_as_str([self.height, self.timestamp, self.target, self.parent_hash, self.is_genesis, self.merkle], sep='`')

    def header(self):
        """ Computes the full header string of a block after mining (includes the seal).

        Returns:
            str: String representation of the block header.
        """
        return encode_as_str([self.unsealed_header(), self.seal_data], sep='`')

    def calculate_hash(self):
        """ Get the SHA256^2 hash of the block header.

        Returns:
            str: SHA256^2 hash of self.header()
        """
        return sha256_2_string(str(self.header()))

    def __repr__(self):
        """ Get a full representation of a block as string, for debugging purposes; includes all transactions.

        Returns:
            str: Full and unique representation of a block and its transactions.
        """
        return encode_as_str([self.header(), "!".join([str(tx) for tx in self.transactions])], sep="`")

    def set_seal_data(self, seal_data):
        """ Adds seal data to a block, recomputing the block's hash for its changed header representation.
        This method should never be called after a block is added to the blockchain!

        Args:
            seal_data (int): The seal data to set.
        """
        self.seal_data = seal_data
        self.hash = self.calculate_hash()

    def is_valid(self):
        """ Check whether block is fully valid according to block rules.

        Includes checking for no double spend, that all transactions are valid, that all header fields are correctly
        computed, etc.

        Returns:
            bool, str: True if block is valid, False otherwise plus an error or success message.
        """

        chain = blockchain.chain # This object of type Blockchain may be useful

        # Placeholder for (1a)

        # (checks that apply to all blocks)
        # Check that Merkle root calculation is consistent with transactions in block (use the calculate_merkle_root function) [test_rejects_invalid_merkle]
        # On failure: return False, "Merkle root failed to match"
        if not self.merkle == self.calculate_merkle_root():
            return False, "Merkle root failed to match"

        # Check that block.hash is correctly calculated [test_rejects_invalid_hash]
        # On failure: return False, "Hash failed to match"
        if not self.hash == self.calculate_hash():
            return False, "Hash failed to match"

        # Check that there are at most 900 transactions in the block [test_rejects_too_many_txs]
        # On failure: return False, "Too many transactions"
        if len(self.transactions) > 900:
            return False, "Too many transactions"

        # (checks that apply to genesis block)
            # Check that height is 0 and parent_hash is "genesis" [test_invalid_genesis]
            # On failure: return False, "Invalid genesis"
        if self.is_genesis:
            if self.height != 0 or self.parent_hash != 'genesis' or  self.hash != self.calculate_hash():
                return False, "Invalid genesis"

        # (checks that apply only to non-genesis blocks)
        else:
            # Check that parent exists (you may find chain.blocks helpful) [test_nonexistent_parent]
            # On failure: return False, "Nonexistent parent"
            if self.parent_hash not in chain.blocks.keys():
                return False, "Nonexistent parent"

            # Check that height is correct w.r.t. parent height [test_bad_height]
            # On failure: return False, "Invalid height"
            parent_block = chain.blocks[self.parent_hash]
            if self.height != (parent_block.height + 1):
                return False, "Invalid height"

            # Check that timestamp is non-decreasing [test_bad_timestamp]
            # On failure: return False, "Invalid timestamp"
            if self.timestamp < parent_block.timestamp:
                return False, "Invalid timestamp"

            # Check that seal is correctly computed and satisfies "target" requirements; use the provided seal_is_valid method [test_bad_seal]
            # On failure: return False, "Invalid seal"
            if not self.seal_is_valid():
                return False, "Invalid seal"

            # Check that all transactions within are valid (use tx.is_valid) [test_malformed_txs]
            # On failure: return False, "Malformed transaction included"
            for tx in self.transactions:
                if not tx.is_valid():
                    return False, "Malformed transaction included"

            # Check that for every transaction
            for tx in self.transactions:
                # the transaction has not already been included on a block on the same blockchain as this block [test_double_tx_inclusion_same_chain]
                # (or twice in this block; you will have to check this manually) [test_double_tx_inclusion_same_block]
                # (you may find chain.get_chain_ending_with and chain.blocks_containing_tx and util.nonempty_intersection useful)
                # On failure: return False, "Double transaction inclusion"
                
                # [test_double_tx_inclusion_same_block]
                tx_hashes = [t.hash for t in self.transactions]
                if len(set(tx_hashes)) != len(tx_hashes):
                    return False, "Double transaction inclusion"            

                # [test_double_tx_inclusion_same_chain]
                block = self
                while block.parent_hash != "genesis":
                    block = chain.blocks[block.parent_hash]
                    if tx.hash in [t.hash for t in block.transactions]:
                        return False, "Double transaction inclusion"
                
                # for every input ref in the tx
                for input_ref in tx.input_refs:
                    # (you may find the string split method for parsing the input into its components)
                    tx_id = input_ref.split(":")[0]
                    output_idx = int(input_ref.split(":")[1])
                    # each input_ref is valid (aka corresponding transaction can be looked up in its holding transaction) [test_failed_input_lookup]
                    # (you may find chain.all_transactions useful here)
                    # On failure: return False, "Required output not found"
                    tx_in_same_block = tx_id in tx_hashes

                    if (not tx_in_same_block and tx_id not in chain.all_transactions):
                        return False, "Required output not found"
                    else:
                        """
                        find target transaction.
                        - from previous block: `chain.all_transactions[tx_id]`
                        - from the same block: `[t for t in self.transactions if t.hash == tx_id][0]`
                        """
                        if tx_id not in chain.all_transactions.keys():
                            target_transaction = [t for t in self.transactions if t.hash == tx_id][0]
                        else:
                            target_transaction = chain.all_transactions[tx_id]
                        # output_idx overflow:
                        output_idx_overflow = (output_idx + 1) > len(target_transaction.outputs)
                        if output_idx_overflow:
                            return False, "Required output not found"
                    # every input was sent to the same user (would normally carry a signature from this user; we leave this out for simplicity) [test_user_consistency]
                    # On failure: return False, "User inconsistencies"
                    previous_output_transaction = target_transaction.outputs[output_idx]
                    this_input_name = previous_output_transaction.receiver
                    this_outputs_names = set([t.sender for t in tx.outputs])
                    if this_input_name not in this_outputs_names or len(this_outputs_names) > 1:
                        return False, "User inconsistencies"
                    this_inputs_names = set([target_transaction.outputs[out_id].receiver for out_id in map(lambda x: int(x.split(":")[1]), tx.input_refs)])
                    if len(this_inputs_names) > 1:
                        return False, "User inconsistencies"

                    # no input_ref has been spent in a previous block on this chain [test_doublespent_input_same_chain]
                    # (or in this block; you will have to check this manually) [test_doublespent_input_same_block]
                    # (you may find nonempty_intersection and chain.blocks_spending_input helpful here)
                    # On failure: return False, "Double-spent input"
                    if input_ref in chain.blocks_spending_input:
                        """
                        double spend on same chain.
                        """
                        having_this_tx_blocks = list(map(lambda x: chain.blocks[x], chain.blocks_spending_input[input_ref]))
                        max_height = max(map(lambda x: x.height, having_this_tx_blocks))
                        if self.height > max_height:
                            return False, "Double-spent input"
                    else:
                        """
                        double spend on same block.
                        """
                        init_input_ref = []
                        for i in self.transactions:
                            if nonempty_intersection(init_input_ref, i.input_refs):
                                return False, "Double-spent input"
                            else:
                                init_input_ref.extend(i.input_refs)

                    # each input_ref points to a transaction on the same blockchain as this block [test_input_txs_on_chain]
                    # (or in this block; you will have to check this manually) [test_input_txs_in_block]
                    # (you may find chain.blocks_containing_tx.get and nonempty_intersection as above helpful)
                    # On failure: return False, "Input transaction not found"
                    if tx_id in list(map(lambda x: x.hash, self.transactions)):
                        pass
                    elif tx_id in chain.all_transactions.keys():
                        """
                        test_input_txs_on_chain
                        """
                        contain_this_tx_blocks = list(map(lambda x: chain.blocks[x], chain.blocks_containing_tx[tx_id]))
                        max_height = max(map(lambda x: x.height, contain_this_tx_blocks))
                        if self.height <= max_height:
                            return False, "Input transaction not found"


                # for every output in the tx
                    # every output was sent from the same user (would normally carry a signature from this user; we leave this out for simplicity)
                    # (this MUST be the same user as the outputs are locked to above) [test_user_consistency]
                    # On failure: return False, "User inconsistencies"
                # the sum of the input values is at least the sum of the output values (no money created out of thin air) [test_no_money_creation]
                # On failure: return False, "Creating money"
                for input_ref in tx.input_refs:
                    tx_id = input_ref.split(":")[0]
                    output_idx = int(input_ref.split(":")[1])
                    if tx_id not in chain.all_transactions.keys():
                        target_transaction = [t for t in self.transactions if t.hash == tx_id][0]
                    else:
                        target_transaction = chain.all_transactions[tx_id]
                    previous_output_transaction = target_transaction.outputs[output_idx]
                    sender_name = previous_output_transaction.receiver
                    money_upper_bound = previous_output_transaction.amount
                    current_transaction_outputs = tx.outputs
                    if sum(map(lambda x: x.amount if x.sender == sender_name else 0, current_transaction_outputs)) > money_upper_bound:
                        return False, "Creating money"


        return True, "All checks passed"


    # ( these just establish methods for subclasses to implement; no need to modify )
    @abstractmethod
    def get_weight(self):
        """ Should be implemented by subclasses; gives consensus weight of block. """
        pass

    @abstractmethod
    def calculate_appropriate_target(self):
        """ Should be implemented by subclasses; calculates correct target to use in block. """
        pass

    @abstractmethod
    def seal_is_valid(self):
        """ Should be implemented by subclasses; returns True iff the seal_data creates a valid seal on the block. """
        pass
