import pandas as pd
import tables

with tables.open_file("file2.hdf5", mode="r") as file:
    records = file.root.people.table.read()

print(records.dtype)

print(records.dtype.names)

