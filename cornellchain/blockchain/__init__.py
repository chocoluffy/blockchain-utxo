import config
from blockchain.chain import Blockchain
import ZODB, ZODB.FileStorage
import transaction

# Setup db and make module globals available
storage = ZODB.FileStorage.FileStorage(config.DB_PATH)
db = ZODB.DB(storage)
connection = db.open()
if not hasattr(connection.root, "blockchain"):
    connection.root.blockchain = Blockchain()
    transaction.commit()

chain = connection.root.blockchain
