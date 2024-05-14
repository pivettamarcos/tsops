from pymongo import MongoClient
import pandas as pd

client = MongoClient('mongodb://%s:%s@127.0.0.1:46529/?directConnection=true' % ("adminuser", "password123"))

db = client['tsops_dev_db']
collection = db['italy']

first_entry = collection.find_one()
print(first_entry)