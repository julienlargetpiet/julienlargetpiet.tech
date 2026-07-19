import pandas as pd

df = pd.DataFrame({
    "country": ["FR", "FR", "EN", "ESP"],
    "PIB": [11, 10.5, 9, 7],
    })

df.to_parquet("dataset_parquet/", 
              partition_cols=["country"])
