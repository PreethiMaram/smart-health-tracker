from db.mongo import collection, users_collection

collection.delete_many({})
users_collection.delete_many({})

print("✅ Database reset")