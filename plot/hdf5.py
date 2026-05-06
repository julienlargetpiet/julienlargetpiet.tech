import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["Paris", "London", "New York"]
})

df.to_hdf("file.hdf5", 
          key="people2", 
          mode="a",
          format="fixed",
          #append=True,
          complib="zlib")

# modes here are w, a 

# keys can be multiple in a single hdf data file
# /a
# /b

df.to_hdf("file2.hdf5", 
          key="people", 
          format="table",
          data_columns=["age"], 
          complib="zlib",
          complevel=0,
          append=True)


# 1. "fixed" (default)
# df.to_hdf("file.h5", key="data", format="fixed")
# 
# 👉 Think: snapshot
# 
# very fast write/read
# stores the whole DataFrame as one block
# ❌ no querying
# ❌ no appending
# 2. "table"
# df.to_hdf("file.h5", key="data", format="table")
# 
# 👉 Think: mini database table
# 
# supports where= queries ✅
# supports append=True ✅
# slower than fixed ❌
# more flexible
# 📊 Structural difference
# 5
# 🧱 Fixed format
# [DataFrame blob]
# one chunk
# no indexing
# no structure for partial reads
# 🧾 Table format
# [Row chunks]
# [Column metadata]
# [Optional indexes]
# chunked storage
# column-aware
# query engine (PyTables)
# ⚡ Practical consequences
# ❌ Fixed cannot do:
# pd.read_hdf(..., where="age > 30")   # ERROR
# ❌ Fixed cannot append:
# df.to_hdf(..., append=True)          # ERROR
# ✅ Table can do both:
# pd.read_hdf(..., where="age > 30")
# 
# df.to_hdf(..., format="table", append=True)
# 🚀 Performance tradeoff
# Feature	fixed ⚡	table 🧠
# Read speed	fastest	slower
# Write speed	fastest	slower
# Query (where)	❌	✅
# Append	❌	✅
# Complexity	low	higher

# With format="table" and no data_columns
# It still supports partial read start, end and also append.





