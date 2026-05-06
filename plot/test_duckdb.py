from sqlalchemy import create_engine, text
import numpy as np
import time, tempfile, os, csv
import pandas as pd
import duckdb

conn = duckdb.connect("test_db.duckdb") 
# if the file does not exist, it creates it before connecting, tat's the database

set_country = ["FR", "EN", "ESP"]
set_location = ["A", "B"]

rng = np.random.default_rng(42)

df = pd.DataFrame({
    "country": rng.choice(set_country, 100_000),
    "location": rng.choice(set_location, 100_000),
    "PIB": rng.normal(3, 15, 100_000),
})

df = df.sort_values("PIB", ascending=False)
df["PIB_bucket"] = (df["PIB"] // 10) * 10

start_write = time.time()

conn.execute("""
CREATE OR REPLACE TABLE table1 AS
SELECT * 
FROM df
""")

conn.commit()

end_write = time.time()

start_read = time.time()

result = conn.execute("""
SELECT * FROM table1
WHERE country='FR'
""").df()

end_read = time.time()


# .fetchdf() = .df()
# .fetchal() -> list of python tuples , one tupple = one row
# .fetchone() -> return a tupple -> the first row

print(result)

conn.close()

print("read: ", end_read - start_read)

print("write: ", end_write - start_write)






