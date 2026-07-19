import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30],
    "city": ["Paris", "London"]
})

df.to_feather("file.feather")
