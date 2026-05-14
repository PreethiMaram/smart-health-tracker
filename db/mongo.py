<<<<<<< HEAD
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["health_db"]

collection = db["users"]          # health data
=======
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["health_db"]

collection = db["users"]          # health data
>>>>>>> 07cb0cbfc6be93d9be7f2b736ba6a03aa51ca954
users_collection = db["accounts"] # login data