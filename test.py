from pymongo import MongoClient
connection_string = "mongodb://test:585394@10.234.173.32:27017/"
client = MongoClient(connection_string)
db = client['test']
cursor1 = db.new.find()
for doc in cursor1:
    print(doc)