from blockchain.util import encode_as_str, sha256_2_string
import persistent

class TransactionOutput(persistent.Persistent):

    def __init__(self, sender, receiver, amount):
        """ Class representing a transaction output in the UTXO model.

        Args:
            sender (str): Account sending (creating) the output.
            receiver (str): Account receiving (and later potentially spending) the output.
            amount (int): Amount being transferred.
        """
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __repr__(self):
        """ Gets unique string representation of an output. """
        return encode_as_str([self.sender, self.receiver, self.amount], sep="~")

class Transaction(persistent.Persistent):

    def __init__(self, input_refs, outputs):
        """ Class representing a transaction in the UTXO model.
        Each transaction consumes (spends) a list of inputs, and creates a list of outputs.

        Args:
            input_refs (:obj:`list` of str): References to every input in the form [tx_hash:list_index_of_output], 0-indexed.
            outputs (:obj:`list` of :obj:`TransactionOutput`): Outputs created by the transaction. An output's index is its position in this list.
        """
        self.input_refs = input_refs
        self.outputs = outputs
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """ Get the hash of the block header.

        Returns:
            str: SHA256^2 hash of the block header.
        """
        return sha256_2_string(str(self.header()))

    def is_valid(self):
        """ Checks if a transaction is well-formed, returning True iff a transaction obeys syntactic rules. """
        return len(self.input_refs) < 10 and len(self.outputs) < 10 and len(self.input_refs) > 0 and len(self.outputs) > 0

    def header(self):
        """ Get string encoding of a transaction's header. """
        return encode_as_str([";".join(self.input_refs), ";".join([str(out) for out in self.outputs])], sep="-")

    def __repr__(self):
        """ Get unique string encoding of a transaction, including its hash (ID). """
        return encode_as_str([self.hash, self.header()], sep="-")
