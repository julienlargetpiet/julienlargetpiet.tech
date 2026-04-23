
For this article, i want to make a Tour over Matplotlib and Seaborn (Seaborn is a super-set of Matplotlib).

Ideed, we often use it not understanding well its architecture and its API.

I want to end this now !

For this article i will use this dataset:

![dataset_sales.csv](../../assets/common_files/Matplotlib/dataset_sales.csv)

Here i just load it andd describe with `pandas`.

```python
import pandas as pd


data = pd.read_csv('dataset_sales.csv',
                   sep = ",",
                   encoding='latin1')

print(data.head(5))
```

Output:

```
   ORDERNUMBER  QUANTITYORDERED  PRICEEACH  ORDERLINENUMBER    SALES        ORDERDATE  ... POSTALCODE  COUNTRY  TERRITORY  CONTACTLASTNAME CONTACTFIRSTNAME  DEALSIZE
0        10107               30      95.70                2  2871.00   2/24/2003 0:00  ...      10022      USA        NaN               Yu             Kwai     Small
1        10121               34      81.35                5  2765.90    5/7/2003 0:00  ...      51100   France       EMEA          Henriot             Paul     Small
2        10134               41      94.74                2  3884.34    7/1/2003 0:00  ...      75508   France       EMEA         Da Cunha           Daniel    Medium
3        10145               45      83.26                6  3746.70   8/25/2003 0:00  ...      90003      USA        NaN            Young            Julie    Medium
4        10159               49     100.00               14  5205.27  10/10/2003 0:00  ...        NaN      USA        NaN            Brown            Julie    Medium
```

Column type.

```
print(data.dtypes)
```

Output:

```
ORDERNUMBER           int64
QUANTITYORDERED       int64
PRICEEACH           float64
ORDERLINENUMBER       int64
SALES               float64
ORDERDATE               str
STATUS                  str
QTR_ID                int64
MONTH_ID              int64
YEAR_ID               int64
PRODUCTLINE             str
MSRP                  int64
PRODUCTCODE             str
CUSTOMERNAME            str
PHONE                   str
ADDRESSLINE1            str
ADDRESSLINE2            str
CITY                    str
STATE                   str
POSTALCODE              str
COUNTRY                 str
TERRITORY               str
CONTACTLASTNAME         str
CONTACTFIRSTNAME        str
DEALSIZE                str
```

`ORDERDATE` is a string, fine we won't use it, but it is good to convert it to datetime format if so.

```python
data["ORDERDATE"] = pd.to_datetime(data["ORDERDATE"])
```

Then:

```
ORDERDATE           datetime64[us]
```

And it is basically clean:

```python

for cl in data.columns:
    na_nb = sum(data[cl].isna())
    print(f"For the column: {cl}: there are: {na_nb} NA cells")
```

Output:

```
For the column: ORDERNUMBER: there are: 0 NA cells
For the column: QUANTITYORDERED: there are: 0 NA cells
For the column: PRICEEACH: there are: 0 NA cells
For the column: ORDERLINENUMBER: there are: 0 NA cells
For the column: SALES: there are: 0 NA cells
For the column: ORDERDATE: there are: 0 NA cells
For the column: STATUS: there are: 0 NA cells
For the column: QTR_ID: there are: 0 NA cells
For the column: MONTH_ID: there are: 0 NA cells
For the column: YEAR_ID: there are: 0 NA cells
For the column: PRODUCTLINE: there are: 0 NA cells
For the column: MSRP: there are: 0 NA cells
For the column: PRODUCTCODE: there are: 0 NA cells
For the column: CUSTOMERNAME: there are: 0 NA cells
For the column: PHONE: there are: 0 NA cells
For the column: ADDRESSLINE1: there are: 0 NA cells
For the column: ADDRESSLINE2: there are: 2521 NA cells
For the column: CITY: there are: 0 NA cells
For the column: STATE: there are: 1486 NA cells
For the column: POSTALCODE: there are: 76 NA cells
For the column: COUNTRY: there are: 0 NA cells
For the column: TERRITORY: there are: 1074 NA cells
For the column: CONTACTLASTNAME: there are: 0 NA cells
For the column: CONTACTFIRSTNAME: there are: 0 NA cells
For the column: DEALSIZE: there are: 0 NA cells
```

And no dupplicates.

```python
nb_dp = sum(data.duplicated(subset=set_of_columns))

print(f"The dataframe contans: {nb_dp} dupplicates")
```

Output:

```
The dataframe contains: 0 dupplicates
```

## First contact

Before plotting something we got to define the "scene" where all plots will be saved.

We do it via `subplots`.

```python
fig, axis = plt.subplots(4, 2,
                      figsize=(15, 15))
```

The scene is called a "figure" (`fig`) and contains a 2 dimensional list of `axis`.

Here the list is:

```
[
    [ax1, ax2],
    [ax3, ax4],
    [ax5, ax6],
    [ax7, ax8],

]
```

One of the first thing we all did using Matplotlib was to plot some quantitative data x and y.

Here we plot te ensual revenue.

```python
r_month = data.groupby("MONTH_ID")["CA_TOTAL"].sum()

axis[1][0].plot(r_month.index, 
                r_month.values, 
                marker="*", 
                linestyle="dashed",
                color="blue")

```

![plot1.png](../../assets/common_files/Matplotlib/plot1.png)

And BOOM! 

A huge mess with positional (x and y) arguments AND keyword arguments (`marker`, `linestyle`...).

Why is that ?

Because of weird thing we can do with matplotlib.

Imagine plotting 2 or more lines.

For example here, we want to plot 0.5% of the comands per month alogside what we just plotted:

```python
commands_m = data.groupby("MONTH_ID").size()
commands_m *= 0.005 * ca_mensuel.mean()
```

## Small point about data types

Quick parenthesis.

Here we used `.size()` that just returns the number of row in each group instead of `.count()` because `.count()` returns the number of non-nul values **for each column**.

Like this:

```python
          ORDERNUMBER  QUANTITYORDERED  PRICEEACH  ORDERLINENUMBER  SALES  ...  CONTACTLASTNAME  CONTACTFIRSTNAME  DEALSIZE  CA_TOTAL  CA_PAR_PRODUIT
MONTH_ID                                                                   ...
1                 229              229        229              229    229  ...              229               229       229       229             229
2                 224              224        224              224    224  ...              224               224       224       224             224
3                 212              212        212              212    212  ...              212               212       212       212             212
4                 178              178        178              178    178  ...              178               178       178       178             178
5                 252              252        252              252    252  ...              252               252       252       252             252
6                 131              131        131              131    131  ...              131               131       131       131             131
7                 141              141        141              141    141  ...              141               141       141       141             141
8                 191              191        191              191    191  ...              191               191       191       191             191
9                 171              171        171              171    171  ...              171               171       171       171             171
10                317              317        317              317    317  ...              317               317       317       317             317
11                597              597        597              597    597  ...              597               597       597       597             597
12                180              180        180              180    180  ...              180               180       180       180             180
```

And it also returns a `pandas.DataFrame` contrary to `.sum()` that returns a `pandas.Series`.

And for plotting here we can work with raw lists `[...]` or `pandas.Series`, because they provide `.index` and `.values`.

A `pandas.Series` is basically a dict, a value asociated to a key.

The key can be lone or a tupple like in this example:

```python
revenue_detailed = data.groupby(["COUNTRY", "DEALSIZE"])["CA_TOTAL"].sum()

cur_country = None

for (country, dealsize), ca in revenue_detailed.items(): 
    if country != cur_country:
        cur_country = country
        print(f"--- Country: {country} --- ")
    print(f"Dealsize: {dealsize} - CA: {ca}")

```

`.items()` just outputs a **tupple** `(key, value)`, and in this case the key itself is a tuple `(country, dealsize)` (we decompose it in the loop).

Output:

```
--- Country: Australia ---
Dealsize: Large - CA: 30100.0
Dealsize: Medium - CA: 305856.96
Dealsize: Small - CA: 185641.5
--- Country: Austria ---
Dealsize: Large - CA: 22100.0
Dealsize: Medium - CA: 107825.14
Dealsize: Small - CA: 42867.909999999996
--- Country: Belgium ---
Dealsize: Medium - CA: 58744.17
Dealsize: Small - CA: 35784.71
--- Country: Canada ---
Dealsize: Large - CA: 4700.0
Dealsize: Medium - CA: 112748.98
Dealsize: Small - CA: 76055.36
...
```

Sometimes you will see `.reset_index()` function call on a `pandas.Series`.

It will **return** a **dataframe** keeping keys (and columns inside what makes the key) and values as columns.

```python
df_revenue_detailed = revenue_detailed.reset_index() 
print(df_revenue_detailed.head())
print(type(df_revenue_detailed))
```

Output:

```
     COUNTRY DEALSIZE   CA_TOTAL
0  Australia    Large   30100.00
1  Australia   Medium  305856.96
2  Australia    Small  185641.50
3    Austria    Large   22100.00
4    Austria   Medium  107825.14
<class 'pandas.DataFrame'>
```

To manipulate a `pandas.Series`, that's simple.

- creation -> `x = pd.Series(["A", "B", "C"], [1, 2, 3])` (values, indices)

- random access -> `x[N]`

- return the reverse -> `x[::-1]` (in place with `.reverse()` does not exist for series)

Why indices ?

To have a landmark on the rows.

Imagine you are slicing inside a PandasDataframe and their order matters (time series) --> You are not forced to manualy create an id (datetime) column, **all is encoded** inside the object itself.

that is a STRONG design choice of Pandas that i personaly hate but i see why it is loved (especialy with pythoners).

Example:

```python
y1 = pd.Series(["A", "B", "C", "D"], [0, 1, 2, 4])

y2 = pd.Series(["A", "B", "C", "D"], [1, 2, 3, 4])

y3 = pd.concat([y1, y2],
               axis=1) # again, it mixes up positional and keyword argument, what a mess !!!

print(y3)

```

- `axis = 0` -> append y2 to y1 -> return a `pandas.Series`

- `axis = 1` -> concat by row -> returns a `pandas.Dataframe`


```python
      0    1
1    A    B
2    B    C
3    C    D
4    D  NaN
0  NaN    A

```

Hmm, now let's find out what will be outputed if we concatenated with `axis = 0` to have a longer `pandas.Series`, i'm curious since there are dupplicated keys `1`, `2` and `3`.

Lets's find out !

```python
y3 = pd.concat([y3, y4], axis=0)

print(y3)
```

Output:

```
1    A
2    B
3    C
4    D
0    A
1    B
2    C
3    D
dtype: str
```

Wow, it actualy worked !

Now, i'm curious about what random access will led to !

```python
prnt(y3[1])
```

Output

```
1    A
1    B
dtype: str
```

Haha, i kew it -> **multimap key** -> conceptually one key -> multiple values

But really a **multimap** ?

Hmm look at that:

```python
print(y3[1])
```

Output.

```
'B'
```

Or even slicing.

```python
print(y3.iloc[1:4])
```

Output.

```
2    B
3    C
4    D
dtype: str
```

It appears that it also can act as positional indexing.

Then, is it more exotic that just:

```
labels -> [Label1..LabelN]
indices -> [0..N]
```

You tell me...

## Random access, `loc` and `iloc`

Take this Series.

```python
s = pd.Series(["A","B","C", "D", "E", "F"], 
              index=[1, 10, 3, 3, 4, 5])
```

We'll use `.iloc[X]` method first, that's simple, just outputs the value at the positional index `X`.

- Note that it's not a function we're **calling** (no `()`) here but rather just **using** a sub-datastructure.

```python
s.iloc[1]
```

Output:

```
'B'
```

Now, with `.loc[X]` -> give me the value that matches the `index` `X`.

```python
s.loc[1]
```

Output:

```
'A'
```

Or

```python
s[3]
```

Output:

```
3    C
3    D
dtype: str
```

Note, here it is a `pandas.Series` because multiple values attached to the same key.

Now, Random Access.

```python
s[1]
```

Output:

```
'A'
```

Or

```python
s[3]
```

Output:

```
3    C
3    D
dtype: str
```

Note, also `pandas.Series`.

But, where it differe is **slices**.

```python
print(s[0:3])
```

Output:

```
1     A
10    B
3     C
dtype: str
```

--> Acts like `.iloc[0:3]` -> positional slices -> `0, 1, 2` -> `pandas.Series`

Now you guess what will hapen with `.loc[3:5]` for example --> multiple `.loc[]` (`.loc[3]` + `.loc[4]`)

```python
s.loc[3:5]
```

Output:

```
3    C
3    D
4    E
5    F
dtype: str
```

(`pandas.Series`)

Annnnnd... it also took `5` (applied `.loc[5]` too) (inconsistency weirdness)

## Invariant with `.loc` slicing

If i have:

```python
s = pd.Series(["F", "A","B","C", "D", "E"], index=[5, 1, 10, 3, 3, 4])
```

Then maybe you think there is no dfference when i apply `s.loc[3:5]`.

Nop, it will just break *silently* lol, because the index is not sorted.

```python
s.loc[3:5]
```

Output:

```
Series([], dtype: str)
```

## Would you mind take some DataFrame ?

You can create a DataFrame in multiple ways.

First, by reading a `CSV`.

```python
df = pd.read_csv("example.csv",
                 sep=",",
                 encoding="latin1")
```

`PARQUET` file.

You know the one that store data compressed and as:

```
- col1
- col2
```

Expanding to:

```
["Julien", "Lucas", "Antoine"]
[0, 1, 2]
```

But compressed.

Really good for ingestion speed, it is a no match agains CSV (no byte jumps + SIMD).

```python
df = read_parquet("example.parquet")
```

--> You can also put `columns=["col1", "col2"]` or `columns=[5, 3, 5]` for example.

--> `use_threads=True`


Its super-power are **filters** while ingesting data.

```python
df = pd.read_parquet(
    "data.parquet",
    filters=[("age", ">", 30)]
)
```

Generic Table (twin of `pd.read_csv()`)

```python
df = pd.read_csv("example.csv",
                 sep=",",
                 encoding="latin1")
```

The only change is the default value of `sep` which is set to a **tabulation** `\t`.

You can also specify from which line yo begin to read with `header=2` for example -> here the header is the **second** line and the data will begn at the third row..

You can also specify the columns you want to read with `usecols`.

Like `usecols=["col1", "col2"]` or with indices `usecols=["col1", "col2"]`.

Example:

```python
df = pd.read_table("data_sales.csv", 
                    sep=",", 
                    usecols=[0, 3, 4], 
                    encoding="latin1")
print(df)
```

Output.

```
      ORDERNUMBER  ORDERLINENUMBER    SALES
0           10107                2  2871.00
1           10121                5  2765.90
2           10134                2  3884.34
3           10145                6  3746.70
4           10159               14  5205.27
...           ...              ...      ...
2818        10350               15  2244.40
2819        10373                1  3978.51
2820        10386                4  5417.57
2821        10397                1  2116.16
2822        10414                9  3079.44

[2823 rows x 3 columns]
```

Or:

```
df = pd.read_table("data_sales.csv", 
                     sep=",", 
                     usecols=["ORDERNUMBER", 
                              "ORDERLINENUMBER", 
                              "SALES"], 
                     encoding="latin1")

print(df)
```

-> Same output.

Then, this does not work.

```python
df = pd.read_table("data_sales.csv", 
                   sep=",", 
                   usecols=[
                            "ORDERNUMBER", 
                            "ORDERLINENUMBER", 
                            "SALES"
                            ], 
                   encoding="latin1", 
                   header=1)
```

--> Error because unable to find the columnname at row = 1, this is expected because they are at row = 0.

But this works.

```python
df = pd.read_table("data_sales.csv", 
                   sep=",", 
                   usecols=[
                            0, 
                            3, 
                            4
                            ], 
                   encoding="latin1", 
                   header=1)

```

Because it just don't care about the names.

(columns names = values here)

Quote handling is also very important !

Take this file for eample:

```
name,age,city
"Alice",25,"Paris"
"Bob",30,"New York, USA"
```

The column separator is `,`, but wealso find it inside the values for City, then we specify `quote="\""` (default values).

```pyhon
data = pd.read_table("file2.csv", 
                     sep=",", 
                     encoding="latin1", 
                     header=0, 
                     quotechar="\"")
```

If your queted values have quote themselves, be sure to double quote them, that is the `CSV` standard.

So:

```
name,age,city
"Alice",25,"Paris"
"Bob",30,"New York, ""USA"""
```

--> Ok

```
name,age,city
"Alice",25,"Paris"
"Bob",30,"New York, "USA""
```

--> Wrong

Escape char is also something very important.

Look, even if you CSV is single quoting iside queted value, you can put `escapechar="\\"` which tells the Pandas Df engine to threat the next character to `\` as a normal character even if it has a special meaning (example quotes).

```
name,age,city
"Alice",25,"Paris"
"Bob",30,"New York, \"USA\""
```

```pyhton
df = pd.read_table("file2.csv", 
                   sep=",", 
                   encoding="latin1", 
                   header=0, 
                   quotechar="\"", 
                   escapechar="\\")

print(df)
```

Output.

```
    name  age             city
0  Alice   25            Paris
1    Bob   30  New York, "USA"
```

`FWF` file

It is a file with no delimiters but each column is spaced by a constant space.

Example:

```
Alice     025Paris     
Bob       030London    
Charlie   035New York  
```

1. Name -> 10 chars (if shorter than 10 chars, then white space) 

2. Age (3 characters) City

3. City -> Same as Name

```python
df = pd.read_fwf("file.fwf")
print(df)
```

Output:

```
     Alice     025Paris
0      Bob    030London
1  Charlie  035New York
```

Ha, it looks that it did not infere well spacing between Age and City, which is normal since there is not obvious spacing, they are contiguous.

Then we can specifyourselves with `colspecs` option.

```pyhton
data = pd.read_fwf("file.fwf", 
                   colspecs=[(0, 10), (10,13), (13,23)])

print(data)
```

Output:

```
     Alice  025     Paris
0      Bob   30    London
1  Charlie   35  New York
```

It also supports `quotechar` and `usecols`.

`JSON`

Best file is one row -> All cols contained on the same level, in one JSON object (`[]`).

```
[
  {"name": "Alice", "age": 25, "city": "Paris"},
  {"name": "Bob", "age": 30, "city": "London"},
  {"name": "Charlie", "age": 35, "city": "New York"}
]
```

Then it's as simple as:

```python
df = pd.read_json("file.json")
print(df)
```

Output.

```
      name  age      city
0    Alice   25     Paris
1      Bob   30    London
2  Charlie   35  New York
```

But sometimes, it is more intricated, like so:

```
[
  {"name": "Alice", "info": {"age": 25, "city": "Paris"}},
  {"name": "Bob", "info": {"age": 30, "city": "London"}}
]
```

```pyhton
df = pd.read_json("file.json")
print(df)
```

Output.

```
    name                           info
0  Alice   {'age': 25, 'city': 'Paris'}
1    Bob  {'age': 30, 'city': 'London'}
```

It's not what we want, so we export to a list of dicts (each row) object and then apply `.json_normalize()`:

```pyton
data = df.to_dict(orient="records")
```

Output:

```
[{'name': 'Alice', 'info': {'age': 25, 'city': 'Paris'}}, {'name': 'Bob', 'info': {'age': 30, 'city': 'London'}}]
```

And then normalization:

```pyton
df = pd.json_normalize(data)
print(df)
```

Output:

```
    name  info.age info.city
0  Alice        25     Paris
1    Bob        30    London
```

But here is the thing, we can avoid the extra step of constructing an intermediate DataFrame object.

We just load raw JSON file and ten apply normalization.

All in `json` ecosystem apart from last step.

```python
import json

with open("file.json") as f:
    data = json.load(f)

df = pd.json_normalize(data)

print(df)
```

Output.

```
    name  info.age info.city
0  Alice        25     Paris
1    Bob        30    London
```

And if we got this kind of intrication:

```
{
  "users": [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30}
  ]
}
```

Then we still load the file with `json.load()`, but after in the noralization we specify the record path.

```python
import json

with open("file.json") as f:
    data = json.load(f)

df = pd.json_normalize(data,
                       record_path="users")

print(df)
```

Output.

```
    name  age
0  Alice   25
1    Bob   30
```

And a very common `JSON` file pattern you can find is to have multipe `JSON` object in the same file, one for each row.

```
{"name": "Alice", "age": 25}
{"name": "Bob", "age": 30}
```

Then here we do:

```python
df = pd.read_json("file.json", lines=True)
print(df)
```

Output.

```
    name  age
0  Alice   25
1    Bob   30
```

`HTML` table, Seriously

Consider this file.

```
<html>
  <body>
    <table>
      <tr>
        <th>name</th>
        <th>age</th>
        <th>city</th>
      </tr>
      <tr>
        <td>Alice</td>
        <td>25</td>
        <td>Paris</td>
      </tr>
      <tr>
        <td>Bob</td>
        <td>30</td>
        <td>London</td>
      </tr>
    </table>


    <table>
      <tr>
        <th>name</th>
        <th>age</th>
        <th>city</th>
      </tr>
      <tr>
        <td>Alice</td>
        <td>25</td>
        <td>Paris</td>
      </tr>
      <tr>
        <td>Bob</td>
        <td>30</td>
        <td>London</td>
      </tr>
    </table>


  </body>
</html>
```

For this one you'll have to install `lxml`.

```
pip install lxml
```

Here you wil read as a table, a table is a list of DataFrames (because an HTML file can contain multiple DataFrames like the one we see).

```python
tables = pd.read_html("file.html")

print(tables)
```

Output

```
[    name  age    city
0  Alice   25   Paris
1    Bob   30  London,     name  age    city
0  Alice   25   Paris
1    Bob   30  London]
```

```python
print(tables[0])
```

```
    name  age    city
0  Alice   25   Paris
1    Bob   30  London
```

Note, that `"file.html"` is obviously a string representing a file, but you can even pass raw string vlue directly representing data.

To do this we have to make the string behave like a file using `StringIO` from `io`.

```python
import pandas as pd
from io import StringIO

html = """
<table>
  <tr><th>name</th><th>age</th><th>city</th></tr>
  <tr><td>Alice</td><td>25</td><td>Paris</td></tr>
  <tr><td>Bob</td><td>30</td><td>London</td></tr>
</table>
"""

df = pd.read_html(StringIO(html))[0]
print(df)
```

Output.

```
    name  age    city
0  Alice   25   Paris
1    Bob   30  London
```

`FEATHER` format.

Same as `PARQUET` but not compressed -> quicker for ingesting data.

For this one you'll need to install `pyarrow`.

```bash
pip install pyarrow
```

It is a binary file too (like `PARQUET`) si i can not show it no sense, so i can make an export of an actualy understable data.

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30],
    "city": ["Paris", "London"]
})

df.to_feather("file.feather")
```

And afer export, we read it as:

```python
df = pd.read_feather("file.feather")
print(df)
```

Output

```
    name  age    city
0  Alice   25   Paris
1    Bob   30  London
```

--> You can also put `columns=["col1", "col2"]` or `columns=[5, 3, 5]` for example.

--> `use_threads=True`

Manualy ingest local data. (`pd.DataFrame()`)

**Al files can be remote on a server with `https://domainname.com/path-to-file`**

To read `xls`/`xlsx` files, you do it via `pd.read_excel("data.xlsx")` or `pd.read_excel("data.xls")`.

Select a sheet via `sheet_name="Sheet1"`or even multiple sheets `sheet_name=["Sheet1", "Sheet2"]`.

- Dict

```python
data = {
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35]
}

df = pd.DataFrame(data)
```

- Even a list of Dicts

But first, let me tell you i donot see where it is valuable to store data as a list of dicts.

Seriousy you are wasting so much memories, by **repeating** the columns on EACH ROW.

```python
data = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
    {"name": "Charlie", "age": 35}
]

df = pd.DataFrame(data)
```

- Lists of Lists

Here you encode the column name as the first value of each python list.

```python
data = [
    ["name", "Alice", "Bob", "Charlie"],
    ["age", 25, 30, 35]
]

df = pd.DataFrame(data)
```

## Going back to plot

We can do it the "clasical" way:

```python

```












