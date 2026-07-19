import numpy as np
import pandas as pd
import duckdb, time
import pyarrow as pa
import time

set_country = ["FR", "EN", "ESP"]
set_location = ["A", "B"]

rng = np.random.default_rng(42)

strt = time.time()

df = pd.DataFrame({
    "country": rng.choice(set_country, 100_000),
    "location": rng.choice(set_location, 100_000),
    "PIB": rng.normal(3, 15, 100_000),
})

end = time.time()

print("time_creation: ", end - strt)

df = df.sort_values("PIB", ascending=False)
df["PIB_bucket"] = (df["PIB"] // 10) * 10

df = df.sort_values("PIB", ascending=False).reset_index(drop=True) #instead of keeping the old index in a new row, we throw them away

print(df.columns)
print(type(df.columns))
#print(df.columns.index)
print(df.index, end="\n\n")

table = pa.Table.from_pandas(df, 
                             preserve_index=False # do not write df index as a pyarrow column
                            )

print(table)
