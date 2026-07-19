import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

set_country = ["FR", "EN", "ESP"]
set_location = ["A", "B"]


#df = pd.DataFrame({
#    "country": [set_country[int(i)] for i in np.round(np.random.uniform(0, 2, 100_000), 0)],
#    "location": [set_location[int(i)] for i in np.round(np.random.uniform(0, 1, 100_000), 0)],
#    "PIB": np.random.normal(3, 15, 100_000),
#    })

df = pd.DataFrame({
    "country": np.random.choice(set_country, 100_000),
    "location": np.random.choice(set_location, 100_000),
    "PIB": np.random.normal(3, 15, 100_000),
    })

df = df.sort_values("PIB", ascending=False)
df["PIB_bucket"] = (df["PIB"] // 10) * 10

table = pa.Table.from_pandas(df)

pq.write_to_dataset(table,
                    root_path = "dataset_parquet4/",
                    partition_cols=["PIB_bucket"],
                    row_group_size=5_000,
                    use_threads=True
                    )

df = pd.read_parquet("dataset_parquet4/",
                     columns=["country", "PIB"],
                     filters=[
                              [
                                ("PIB_bucket", ">=", 10),
                                ("PIB", ">=", 11), 
                                ("PIB", "<=", 13)
                              ]
                             ]
                     )

print(df)

#df.to_parquet("dataset_parquet3/", partition_cols=["location", "country"])

