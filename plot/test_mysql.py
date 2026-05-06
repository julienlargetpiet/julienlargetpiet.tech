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

start_write = time.time()

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method="multi",
    chunksize=10_000,
)

end_write = time.time()

with engine.begin() as conn:
    conn.execute(text("CREATE INDEX idx_table1_country ON table1 (country)"))

start_read = time.time()

with engine.connect() as conn:
    out = pd.read_sql(
        text("SELECT * FROM table1 WHERE country = :country"),
        conn,
        params={"country": "FR"},
    )

end_read = time.time()

print(out)
print("write:", end_write - start_write)
print("read:", end_read - start_read)
print("rows:", len(out))



# equivalent to
# LOAD DATA INFILE '/path/to/data.csv'
# INTO TABLE table1
# FIELDS TERMINATED BY ','
# ENCLOSED BY '"'
# LINES TERMINATED BY '\n'
# IGNORE 1 ROWS
# (country, location, PIB, PIB_bucket);
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

# So this kind of PostgreSQL pattern works:
# 
# buffer = io.StringIO()
# cursor.copy_expert("COPY table FROM STDIN WITH CSV", buffer)
# 
# because PostgreSQL has a STDIN streaming protocol.
# 
# But MySQL’s bulk loader is:
# 
# LOAD DATA LOCAL INFILE '/path/to/file.csv'
# INTO TABLE table1 ...
# 
# So with MySQL, you generally need a real path.
# 
# Why StringIO does not directly work
# 
# StringIO is just an in-memory Python object. MySQL does not know how to read it because SQL only sees:
# 
# LOAD DATA LOCAL INFILE 'some_filename'
# 
# The DB driver then opens/streams that local filename to the server. There is no standard LOAD DATA FROM STDIN equivalent like PostgreSQL COPY FROM STDIN.

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


