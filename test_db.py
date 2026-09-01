"""
Check the MongoDB Atlas connection on its own, before running the web app.

Run with: python test_db.py
"""

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

uri = os.getenv("MONGODB_URI")
if not uri:
    raise SystemExit("MONGODB_URI is not set. Create your .env file first.")

db_name = os.getenv("DB_NAME", "SignUp")
collection_name = os.getenv("COLLECTION_NAME", "users")

client = MongoClient(uri, server_api=ServerApi("1"), serverSelectionTimeoutMS=10_000)
collection = client[db_name][collection_name]

client.admin.command("ping")
print("Ping succeeded.")

result = collection.insert_one({"ownername": "connection-test", "petname": "temp"})
print(f"Inserted test document: {result.inserted_id}")

print(f"Documents now in {db_name}.{collection_name}: {collection.count_documents({})}")

collection.delete_one({"_id": result.inserted_id})
print("Test document removed. Everything works.")
