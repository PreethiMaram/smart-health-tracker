import pandas as pd
import numpy as np

np.random.seed(42)

rows = 10000
data = []

for _ in range(rows):
    sleep = np.random.randint(4, 10)
    stress = np.random.randint(1, 10)
    activity = np.random.randint(1, 10)
    junk = np.random.randint(1, 10)
    water = np.random.randint(1, 10)

    score = sleep*10 + activity*8 + water*6 - stress*7 - junk*6
    score = max(0, min(100, score))

    if score > 75:
        category = "Good"
    elif score > 50:
        category = "Moderate"
    else:
        category = "Poor"

    data.append({
        "Sleep": sleep,
        "Stress": stress,
        "Activity": activity,
        "JunkFood": junk,
        "Water": water,
        "Category": category
    })

df = pd.DataFrame(data)
df.to_csv("dataset.csv", index=False)

print("✅ Dataset generated")