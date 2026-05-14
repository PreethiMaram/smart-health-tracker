import pandas as pd
from db.mongo import collection

collection.delete_many({})

df = pd.read_csv("dataset.csv")
collection.insert_many(df.to_dict("records"))

print("✅ Data inserted")