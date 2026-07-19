import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import time, tempfile, os, csv

engine = create_engine(
    "mysql+pymysql://juju:password@localhost:3306/test_db",
    connect_args={
        "local_infile": True,
    },
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

#start_write = time.time()
#
#df.to_sql(
#    "table1",
#    engine,
#    if_exists="replace",
#    index=False,
#    method=None,
#    chunksize=10_000,
#)

#df.to_sql(
#    "table1",
#    engine,
#    if_exists="replace",
#    index=False,
#    method="multi",
#    chunksize=10_000,
#)

#end_write = time.time()

#with engine.begin() as conn:
#    conn.execute(text("CREATE INDEX idx_table1_country ON table1 (country)"))
#
#start_read = time.time()
#
#with engine.connect() as conn:
#    out = pd.read_sql(
#        text("SELECT * FROM table1 WHERE country = :country"),
#        conn,
#        params={"country": "FR"},
#    )
#
#end_read = time.time()

#print("write:", end_write - start_write)

def mysql_load_data_insert(table, conn, keys, data_iter):
    
    dbapi_conn = conn.connection
    cursor = dbapi_conn.cursor()

    writer_df = pd.DataFrame(data_iter, columns=keys)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        newline="",
    ) as tmp:
        tmp_path = tmp.name
        writer_df.to_csv(
            tmp,
            index=False,
            header=False,
            quoting=csv.QUOTE_MINIMAL,
        )

    columns = ", ".join(f"`{k}`" for k in keys)
    table_name = table.name

    sql = f"""
        LOAD DATA LOCAL INFILE '{tmp_path}'
        INTO TABLE `{table_name}`
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        ({columns})
    """

    try:
        cursor.execute(sql)
    finally:
        os.remove(tmp_path)

start_write = time.time()

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method=mysql_load_data_insert
)

end_write = time.time()

print("write2:", end_write - start_write)


