import tables

class Person(tables.IsDescription):
    name = tables.StringCol(20)
    age = tables.Int32Col()
    city = tables.StringCol(20)

with tables.open_file("file.h5", mode="w") as file:
    table = file.create_table("/", "people", Person)

    row = table.row
    row["name"] = "Alice"
    row["age"] = 25
    row["city"] = "Paris"
    row.append()

    table.flush()
