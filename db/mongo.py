from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["health_db"]

collection = db["users"]          # health data
users_collection = db["accounts"] # login data