import numpy as np
import pandas as pd
import duckdb, time
import pyarrow as pa
import time

set_country = ["FR", "EN", "ESP"]
set_location = ["A", "B"]

rng = np.random.default_rng(42)

strt = time.time()

table = pa.table({
    "country": rng.choice(set_country, 100_000),
    "location": rng.choice(set_location, 100_000),
    "PIB": rng.normal(3, 15, 100_000),
})

end = time.time()

print("time: ", end - strt)

print(table)
