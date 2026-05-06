import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import time, io

engine = create_engine(
    "postgresql+psycopg2://juju:password@localhost:5432/test_db"
)

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

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method="multi",
    chunksize=10_000, 
)

# chunksize
# instead of 
# INSERT INTO table1 (A,B,C)
# VALUES (V1,V2,V3);
# we got batched version in batched versions:
# INSERT INTO table1 (A,B,C)
# VALUES (V1,V2,V3),
# VALUES (V4,V5,V6),
# ...
# VALUES (VN-2,VN-1,VN);
# avoid multiple bacjk and forth between con and db / conn issuing more requests than necessary

end_write = time.time()

with engine.begin() as conn:
    conn.execute(text("CREATE INDEX idx_table1_country ON table1 (country)"))

# engine.begin() is like engine.connect() + conn.commit() if no err else rollback

# So this:
# with engine.connect() as conn:
#     try:
#         conn.execute(text("CREATE INDEX idx_table1_country ON table1 (country)"))
#         conn.commit()
#     except:
#         conn.rollback()
#         raise
# is equivalent of:
# with engine.begin() as conn:
#     conn.execute(text("CREATE INDEX idx_table1_country ON table1 (country)"))
# But for more than one transaction, we should do:
# one with statement -> one transaction
# or
# with engine.connect() as conn:
#     trans = conn.begin()
#     try:
#         conn.execute(text("TRANSACTION1"))
#         trans.commit()
#     except:
#         trans.rollback()
#         raise
# 
#     trans = conn.begin()
#     try:
#         conn.execute(text("TRANSACTION2"))
#         trans.commit()
#     except:
#         trans.rollback()
#         raise
# 
# or simply
# 
# with engine.connect() as conn:
#     try:
#         conn.execute(text("TRANSACTION1"))
#         conn.commit()
#     except:
#         conn.rollback()
#         raise
# 
#     try:
#         conn.execute(text("TRANSACTION2"))
#         conn.commit()
#     except:
#         conn.rollback()
#         raise
# 
# or commit at the end but bad prative because each transaction can fail and you have to have a rollback logic
# that is for WRITE transaction, read does not need rollback, but still good error handling

start_read = time.time()

with engine.connect() as conn:
    out = pd.read_sql(
        text("SELECT * FROM table1 WHERE country = :country"),
        conn,
        params={"country": "FR"},
    )

end_read = time.time()

print(out)
print("write1:", end_write - start_write)
print("read:", end_read - start_read)
print("rows:", len(out))

# creating custom method
# COPY avoids multiple INSERT, just one stdin -> db stream transfer
# equivament to:
# COPY table1 (country, location, pib, pib_bucket)
# FROM '/absolute/path/data.csv'
# WITH (
#     FORMAT csv,
#     HEADER true,
#     DELIMITER ',',
#     NULL ''
# );
def psql_copy_insert(table, conn, keys, data_iter):
    """
    Custom insertion method for pandas.DataFrame.to_sql(..., method=...).

    table: pandas SQLTable object
    conn: SQLAlchemy connection
    keys: column names, that are the columns selected at df[[...]].to_sql(...) time, for df.to_sql(...) -> all columns
    data_iter: rows iterator

    Internally, this custom methods receives those args inside to_sql(...)
    """
    dbapi_conn = conn.connection
    cursor = dbapi_conn.cursor()

    buffer = io.StringIO()
    writer_df = pd.DataFrame(data_iter, columns=keys)
    writer_df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    columns = ", ".join(f'"{k}"' for k in keys)
    table_name = table.name

    sql = f'COPY "{table_name}" ({columns}) FROM STDIN WITH CSV'

    cursor.copy_expert(sql=sql, file=buffer)

start_write = time.time()

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method=psql_copy_insert,
)

end_write = time.time()

print("write2:", end_write - start_write)

df = conn.execute(
"""
SELECT * FROM table1
"""
).fetchdf()

print(df)




