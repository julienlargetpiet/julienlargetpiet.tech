
Welcome to this introduction (part 1) to data-analysis in Python with `pandas`, a it of `numpy`, `Matplotlib` and its wrapper `Seaborn`.

For this article I will use this dataset:

![data_sales.csv](../../assets/common_files/Matplotlib/data_sales.csv)

Here I just load it andd describe with `pandas`.

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

We will also create a column named `"REVENUE"`:

```python

if not col_ca in set_of_columns:
    data["REVENUE"] = data["QUANTITYORDERED"] * data["PRICEEACH"]

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

import matplotlib.pyplot as plt

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

One of the first thing we all did using Matplotlib was to plot some quantitative data `x` and `y`.

Here we plot the mensual revenue.

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

Because of a powerfull thing we can do with matplotlib.

Imagine plotting 2 or more lines.

For example here, we want to plot 50% of the mensual revenue alongside what we just plotted:

```python

r_month2 = 0.5 * r_month

axis[1][0].plot(r_month.index, 
                r_month.values, 
                r_month2.index,
                r_month2.values,
                marker="*", 
                linestyle="dashed",
                color="blue")

```

![plot2.png](../../assets/common_files/Matplotlib/plot2.png)

But here both lines will have the same options (color, marker, linestyle), so we can use te string format to precise the options for each lines as the following:

```python

r_month2 = 0.5 * data.groupby("MONTH_ID").sum()

axis[1][0].plot(r_month.index, 
                r_month.values, 
                "b*--",
                r_month2.index,
                r_month2.values,
                "ro-")

```

![plot3.png](../../assets/common_files/Matplotlib/plot3.png)


- `"b*--"` -> `b` -> blue, `*` -> star marker and `--` -> dashed

- `"ro--"` -> `r` -> red, `o` -> circle marker and `-` -> solid line

This is more compact than the 2 function call equivalent:

```python

axis[1][0].plot(r_month.index, 
                r_month.values, 
                "b*--")

axis[1][0].plot(r_month2.index, 
                r_month2.values, 
                "ro-")


```

Or with the explicit variable call (`color = ...` ...).

## Small point about semantic

### On occurence function after `groupby`

Here, we used `.sum()` as the reduction function of the `.groupby(...)`, but we could also compute the occurence of rows inside each group.

And for this goal, we have 2 ways to do it, counting the exact row number just with `.size` attribute or the non-null ( not `Na`, `None`) row number with the `.count()` method, both returns a `pd.Series` (see later).

`size` is an attribute for `pd.Series` and `pd.DataFrame`, but a method in `pd.SeriesGroupBy`.

A `pd.SeriesGroupBy` is the object returned by `.groupby(...)` method, like this:

```python


r_month = data.groupby("MONTH_ID")["CA_TOTAL"]

print(type(r_month))

```

Result:

```

<class 'pandas.api.typing.SeriesGroupBy'>

```

So we can apply:

```python

print(r_month.size())

```

Result:

```

MONTH_ID
1     229
2     224
3     212
4     178
5     252
6     131
7     141
8     191
9     171
10    317
11    597
12    180
Name: CA_TOTAL, dtype: int64

```

### On plotting

And for plotting here we can work with raw lists `[...]` or `pandas.Series` attributes `.index` and `.values`.

A `pandas.Series` is an ordered, one-dimensional labeled array.

- duplicate labels are allowed

- positional ordering matters

- vectorized operations are central

- values have a common dtype or extension dtype

- slicing and alignment follow pandas rules.

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

We have the `.index` attribute which we can think of a list of keys for now (more on this later) (thes `pd.MultiIndex` variant) and the `.values` which is a list of the associated values:

```python

revenue_detailed = data.groupby(["COUNTRY", "DEALSIZE"])["CA_TOTAL"].sum()


print(revenue_detailed.index)

print("###")

print(revenue_detailed.values)

```

Result:

```

MultiIndex([(  'Australia',  'Large'),
            (  'Australia', 'Medium'),
            (  'Australia',  'Small'),
            (    'Austria',  'Large'),
            (    'Austria', 'Medium'),
            (    'Austria',  'Small'),
            (    'Belgium', 'Medium'),
            (    'Belgium',  'Small'),
            (     'Canada',  'Large'),
            (     'Canada', 'Medium'),
            (     'Canada',  'Small'),
            (    'Denmark',  'Large'),
            (    'Denmark', 'Medium'),
            (    'Denmark',  'Small'),
            (    'Finland',  'Large'),
            (    'Finland', 'Medium'),
            (    'Finland',  'Small'),
            (     'France',  'Large'),
            (     'France', 'Medium'),
            (     'France',  'Small'),
            (    'Germany',  'Large'),
            (    'Germany', 'Medium'),
            (    'Germany',  'Small'),
            (    'Ireland',  'Large'),
            (    'Ireland', 'Medium'),
            (    'Ireland',  'Small'),
            (      'Italy',  'Large'),
            (      'Italy', 'Medium'),
            (      'Italy',  'Small'),
            (      'Japan',  'Large'),
            (      'Japan', 'Medium'),
            (      'Japan',  'Small'),
            (     'Norway',  'Large'),
            (     'Norway', 'Medium'),
            (     'Norway',  'Small'),
            ('Philippines',  'Large'),
            ('Philippines', 'Medium'),
            ('Philippines',  'Small'),
            (  'Singapore',  'Large'),
            (  'Singapore', 'Medium'),
            (  'Singapore',  'Small'),
            (      'Spain',  'Large'),
            (      'Spain', 'Medium'),
            (      'Spain',  'Small'),
            (     'Sweden',  'Large'),
            (     'Sweden', 'Medium'),
            (     'Sweden',  'Small'),
            ('Switzerland', 'Medium'),
            ('Switzerland',  'Small'),
            (         'UK',  'Large'),
            (         'UK', 'Medium'),
            (         'UK',  'Small'),
            (        'USA',  'Large'),
            (        'USA', 'Medium'),
            (        'USA',  'Small')],
           names=['COUNTRY', 'DEALSIZE'])
###
[  30100.    305856.96  185641.5    22100.    107825.14   42867.91
   58744.17   35784.71    4700.    112748.98   76055.36   30300.
  108726.63   53721.     22200.    159820.03   86694.67  101348.16
  535615.05  282294.64   18200.    104218.24   56270.84    8200.
   19800.     15237.24   29900.    151579.4   127923.47   13500.
   79021.4    60555.29   22300.    149251.14   74564.66    4200.
   51975.26   24115.91   18400.    137179.5    72406.     83300.
  625811.87  312594.1     6600.    117818.93   49845.17   75208.31
   18136.6    22500.    250103.41  140599.93  300909.75 1810432.26
  875083.2 ]

```

Sometimes you will see `.reset_index()` function call on a `pandas.Series`.

It will reset the index from 0 to the number of rows minus 1 (`0..(N-1)`).

Basically, it replaces the current `index` with a default zero-based `index` and moves the previous index levels into columns unless `drop=True`.

But, what to do with the previous index ?

`pandas` decided to not throw them away but to keep it as separate column(s) (`drop = False`).

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

To create a `pandas.Series`, that's simple.

- creation -> `x = pd.Series(["A", "B", "C"], [1, 2, 3])` (values, indices)

We can of course create them with a dictionary:

```python

pd.Series({0 : "A", 1 : "B", 3 : "C"})

```

Note:

We can't write the equivalent with the `dict(...)` synthax, because they must be ids, and numbers are not ids, hence we can not write:

```python

>>> dict(0 = "A", 1 = "B", 2 = "C")

```

- random access -> `x[N]`

- return the reverse -> `x[::-1]` (in place function with `.reverse()` does not exist for series)

Why indices ?

To have a landmark on the rows.

Imagine you are slicing inside a `PandasDataframe` and their order matters (time series for example) --> You are not forced to manualy create an id (`datetime`) column, **all is encoded** inside the object itself like we'll see later for a specific flavor of `Series`.

You can also apply data-manipulation function choosing the `index` column as if it was a real column, example:

```python

import pandas as pd

df = pd.DataFrame(
    {"value": [10, 20, 30, 40]},
    index=["A", "A", "B", "B"]
)

df.groupby(df.index)["value"].sum()

```

Result:

```python

A    30
B    70
Name: value, dtype: int64

```

And with `pd.MultiIndex` that we'll discuss later, we can chose the index level:

```python

df.groupby(level=0).sum()

# OR

df.groupby(level=["COUNTRY", "DEALSIZE"])["CA_TOTAL"].sum()

```



This is a STRONG design choice of `pandas`.

Other examples:

```python

y1 = pd.Series(["A", "B", "C", "D"], [0, 1, 2, 4])

y2 = pd.Series(["A", "B", "C", "D"], [1, 2, 3, 4])

y3 = pd.concat([y1, y2],
               axis=1)

# again, it mixes up positional and keyword argument, what a mess !!!

print(y3)

```

- `axis = 0` -> append y2 to y1 -> return a `pandas.Series`

- `axis = 1` -> concat by row -> returns a `pandas.Dataframe`


Result:

```python

      0    1
1    A    B
2    B    C
3    C    D
4    D  NaN
0  NaN    A

```

And, from a `pd.DataFrame`:

```python

left = pd.DataFrame(
    {"name": ["Alice", "Bob"]},
    index=[1, 2]
)

right = pd.DataFrame(
    {"score": [90, 85]},
    index=[1, 2]
)

left.join(right)

```

Result:

```

    name  score
1  Alice     90
2    Bob     85

```

You can choose join type of course:

```

left.join(right, how="inner")
left.join(right, how="outer")
left.join(right, how="right")

```

If you has another column on the `left` dataframe, for example `"Id2"` on which you would perform the join with the `index` of the right dataframe, you would tell to the `on=` argument:

```python

left.join(right, how = "inner", on = "Id2")

```

Note that `.join()` methods are bsically synthaxic sugar of `pd.DataFrame.merge()` method or the more general `pd.merge()` method where the right dataframe key column is told to be the `index` (of the right dataframe).

So `pd.merge()` is more general:

```python

>>> left
    name
1  Alice
2    Bob

>>> right
   score  Id2
1     40    1
2     80    2
1     60    1

>>> left.merge(right, left_index = True, right_index = False, right_on = "Id2", how = "inner")
    name  score  Id2
1  Alice     40    1
1  Alice     60    1
2    Bob     80    2

>>> pd.merge(left, right, left_index = True, right_index = False, right_on = "Id2", how = "inner")
    name  score  Id2
1  Alice     40    1
1  Alice     60    1
2    Bob     80    2

```

But, technically, nothing you can not simply do by creating your own `index` column in the data, so why having `index` as a separated related data-structure ?

Because of **selections** !

As you'll see in a moment with all the flavors of the `pd.Index`, selecting rows from a `pd.DataFrame` is peformed through the `index` machinery (conceptually a multimap) and it makes things A LOT easier to work with for all kind of data (`time-series, interval, multi-level` and much more).

In other terms, this is a semantic abstraction level that helps us manipulate all kind of data.

But first, quick note; default index is just `[0, n-1]`.

Second note; you can also create a `pd.Series` of chosen length that is filled with a special value.

```python

x = pd.Series(True, index=[0, 1, 2, 3])
print(x)

```

Output.

```

0    True
1    True
2    True
3    True
dtype: bool

```

Or using the `[X] * N` to create list of length `N`:

```

x = pd.Series([True, False] * 3)
print(x)

```

Output.

```

0     True
1    False
2     True
3    False
4     True
5    False
dtype: bool

```

Hmm, now let's find out what will be outputed if we concatenate with `axis = 0` to have a longer `pandas.Series`, I'm curious since there are dupplicated keys `1`, `2` and `3`.

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

Wow, it actualy worked (index values are not always uniques) !

Now, I'm curious about what random access will led to !

```python

print(y3[1])

```

Output

```

1    A
1    B
dtype: str

```

Haha, I kew it -> **multimap key** -> conceptually one key -> multiple values.

But it's not implemented like that as you'll see in this part [pd.Index](#`pd.Index`)

## Introduction to random access, `loc` and `iloc`

Take this Series.

```python

s = pd.Series(["A","B","C", "D", "E", "F"], 
              index=[1, 10, 3, 3, 4, 5])

```

We'll use `.iloc[X]` method first, that's simple, just outputs the value at the positional index `X`.

- Note that it's not a function we're **calling** (no `()`) here but rather just **using** a the datastructure built-in random access.

```python

s.iloc[1]

```

Output:

```

'B'

```

Now, with `.loc[X]` -> give me the value(s) that matches the `index` `X`.

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

Now, default random access synthax.

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

It acts like `.loc`.

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

Here, another example:

```python

>>> x = pd.Series(list("ABC"), index = [1, 2, 3])

```

Now, we'll apply the range from `1` to `3` on it.

```python

>>> x[1:3]

2    B
3    C
dtype: str

```

We do not have the first key-value pair, because we begin at the **position** `1`, but we have the last one because that is the third position and we told to stop at position `3` which is the fourth element. 

It basically acts like a normal random access through slicing:

```python

>>> lst = list("abcde")

>>> lst[1:5]
['b', 'c', 'd', 'e']

>>> x2 = pd.Series(list("abcde"), index = [1, 2, 3, 4, 5])

>>> x2.iloc[1:5]
2    b
3    c
4    d
5    e
dtype: str

>>> x2[1:5]
2    b
3    c
4    d
5    e
dtype: str

```

So of course, it doesn't care about the `index` order:

```python

>>> x = pd.Series(list("abcde"), index = [1, 4, 2, 5, 6])

>>> x[1:5]
4    b
2    c
5    d
6    e
dtype: str

>>> x.iloc[1:5]
4    b
2    c
5    d
6    e
dtype: str

```

So if we put a boundary that is above the length of the list, it will act as `:`.

Example:

```python

>>> [1, 2][0:44]
[1, 2]



>>> x.iloc[1:44]
2    B
3    C
dtype: str

```

Also a quick note about the behavior of `.iloc[]`.

- `[ID1:ID2]` -> returns a view, but when you modifie it, it silently copies it before writing (Copy On Write) so it never modifies the origin

- `[[ID1, ID2, ...]]` -> returns a copy

We can also visualize the CoW with `numpy.shares_memory()`:

```python

>>> import numpy as np

>>> x = pd.Series([0, 1, 2, 3, 4], index = [1, 10, 5, 2, 8])
>>> y = x.loc[10:2]
>>> np.shares_memory(x.to_numpy(), y.to_numpy())
True

```

And here the `[[...]]` synthax effect.

```python

>>> import numpy as np

>>> yb = x[[10, 5, 2]]
>>> np.shares_memory(x.to_numpy(), yb.to_numpy())
False

```


Now you guess what will happen with `.loc[3:5]` for example --> multiple `.loc[]` (maybe `.loc[3] ++ .loc[4]`)

```python

s = pd.Series(["A","B","C", "D", "E", "F"], 
              index=[1, 10, 3, 3, 4, 5])

>>> s.loc[3:5]

```

Output:

```

3    C
3    D
4    E
5    F

dtype: str
```

Annnnnd... it also took `5` (applied `.loc[5]` too).

The mental model of `.loc[]` for slices random access can be described with pseudo-code:

```python

start_pos = position_of_label(X1)

end_pos = position_of_label(X2)

result = ser.iloc[start_pos:end_pos + 1]

```

This is why the following work like this:

```python

>>> x
1     A
10    B
3     C
3     D
4     E
5     F
dtype: str

>>> x.loc[10:5]
10    B
3     C
3     D
4     E
5     F
dtype: str

# Same as:

>>> x.iloc[1:6]
10    B
3     C
3     D
4     E
5     F
dtype: str

```

## `pd.Index()`

I do not have much more information to discuss here about the valnilla `pd.Index`, so I'll discuss the underlying method that links `.values` and `.index`.

They also support vectorized operation.

```python

x = pd.Index(["julien", "antoine", "lucas", "baptiste"])
print(x.str.upper())

```

Output.

```

Index(['JULIEN', 'ANTOINE', 'LUCAS', 'BAPTISTE'], dtype='str')

```

Lookups are generally `O(1)`.

```python

print(x.get_loc("antoine"))

```

Output.

```

1

```

In fact, we can basically implement `.loc[]` using `.get_loc`.

It is fundamental, it means there isn't a hasmap relation between the `pd.Series.index` and the `pd.Series.Series.values`.

It is all positional relationship (and no matter the `Index` variant we are going to explain).

```python

>>> x

1     A
3     C
3     D
4     E
5     F
10    B
dtype: str

>>> x.index.get_loc(5)

4

>>> x.iloc[x.index.get_loc(3)]

3    C
3    D
dtype: str

```

When it comes to the search algorithm for `ps.Series.index.get_loc` I precise "generally" because for large monotonic `pd.Index`, pandas can switch its searching algorithm to a binary search.

Doing so the execution time increases to `O(log(n))` but it is a more compact data-structure and the `O(n)` time (and memory) for the initialization cost of a hashmap is therefore not paid.

So, it is a balance between how much will we use random access versus the cost paid to construct the underlying data-structure that allow the random access.

Is the hashmap construction amortized by how much I will search in the `pd.Series` ?

We can't control the method used internally.

But you can `.sort_index()` to hint `pandas` to use binary search for example:

```python

>>> x
1     A
10    B
3     C
3     D
4     E
5     F
dtype: str

>>> x = x.sort_index()
>>> x
1     A
3     C
3     D
4     E
5     F
10    B
dtype: str

```

But if the increasing step is constant the best is to use `pd.RangeIndex` as you'll see later.

Also, note that binary search does not require the values to be integer at all, it will use the adapted comparison mechanism for the related type.

It conceptually does:

```python

if key < middle_value:
    search_left_half()
elif key > middle_value:
    search_right_half()
else:
    found()

```

The `<` and `>` can be replaced with whatever function is adapted for the comparison, therefore it's conceptually more like:

```python

if is_lower(key, middle_value):
    search_left_half()
elif is_higher(key, middle_value):
    search_right_half()
else:
    found()


```

But `<`and `>` in Python already work for `str` (lexicographically sorting):

```python

>>> "cazaz" > "baz"
True

>>> "bazaz" > "baz"
True

>>> "aazaz" > "baz"
False

>>> "ab" > "baz"
False

```

That's why it works on a `pd.Index` whose values are string, like this one:

```python

>>> x = pd.Index(list("chabcd"))

>>> x.get_loc("a")
2

```

And if you know that you will perform **many random access** on the same `pd.Series`, you can use an external dictionary (pay the cost once and it's basically free later for all random access):

```python

>>> positions = {label : position for position, label in enumerate(x.index)}

>>> positions

{1: 0, 3: 2, 4: 3, 5: 4, 10: 5}

```

And then use it like:

```python

position = positions[4]

value = x.iloc[position]

```

But doing this, we lose all the rest of the values positions for the non-unique keys, because this is what happen:

```python

positions[1] = 0
positions[3] = 1
positions[3] = 2  # overwrites the previous 1
positions[4] = 3
positions[5] = 4
positions[10] = 5

```

In order to preserve all indices, we can use `collections.defaultdict` wich is a hashmap whose elements typeis configurable, here we'll make them a list:

```

>>> from collections impot defaultdict

>>> positions = defaultdict(list)

>>> for position, label in enumerate(x.index): positions[label].append(position)

```

But doing so, you have to update the hashmap values every time the `pd.Series` is updated, and add a key and set its value if a new index value is added.

So we've seen that the call to the function does not scan the whole array.

We can make two different benchamrks to infere this behavior by the results, one with creating a `pd.Index` whose values are monotonicly sorted, but not by a constant step otherwise it would be automatically converted to a `pd.RangeIndex`, to test the binary search mechanism and one with unsorted `pd.Index` values to test hashmap searrch behavior.

So first, we test the binary search mechanism:

```python

import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 2_000_000, 100_000))
ys = []

n_repeats = 10_000

rng = np.random.default_rng(55)

for n in xs:

    steps = rng.integers(1, 5, size = n)

    idx = pd.Index(np.cumsum(steps))
    keys = rng.choice(idx.to_numpy(), size = n_repeats)

    idx.get_loc(keys[0])

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure0.png")

```

The crucial part is:

```python

steps = rng.integers(1, 5, size = n)

idx = pd.Index(np.cumsum(steps))
keys = rng.choice(idx.to_numpy(), size = n_repeats)

```

It randomly generates `n` integers from `1` to `5`, and from this it computes the cummulated sum for each position.

So we effectively have monotonicly increasing `index` values by a non-constant step, because the later are randomly generated.

And now, from the generetaed `index` values, we randomly choose `n_repeats` keys.

Also, this one:

```python

idx.get_loc(keys[0])

```

It allows to build the hashmap, if this is the used method of course, to not take in count its construction cost.

Note that the keys are all unique because steps lower bound is `1`.

Here are the results:

![measure0.png](../asset/common_files/Matplotlib/measure0.png)

We see that the `elapsed_time` is pretty flat before `n = 1M`, then suddenly jumps to an order of magnitude, and then it slightly increases.

This correspond to this behavior:

```python

if len(index) >= 1_000_000 and index.is_monotonic_increasing:
    return binary_search(key)

build_hash_table_if_needed()
return hash_lookup(key)

```

Now, I want to make another benchmark but on a a non-sorted `pd.Index` to see if it differe from the sorted `pd.Index` (we could deduce that query mechanism is not the same):

```python

import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

xs = list(range(1_000, 2_000_000, 100_000))
ys = []

n_repeats = 10_000

rng = np.random.default_rng(55)

for n in xs:
    
    idx = pd.Index(rng.permutation(n))
    keys = rng.randint(0, n, size = n_repeats)
 
    idx.get_loc(keys[0])

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure2.png")

```

The crucial part is:

```python

idx = pd.Index(rng.permutation(n))

```

It randomly generates a permutation from `0` to `n`, so it includes all keys, theay are also all distinct as the first benchmark.

Here are examples of `numpy.random.permutation()`

```

>>> import numpy as np

>>> rng = np.random.default_rng(5)

>>> rng.permutation(44)

array([ 6, 20, 41,  9, 22, 12, 27, 23, 28, 18,  2, 26, 17, 38, 42, 30, 33,
        7, 39, 43, 11, 13, 19, 31, 32, 24, 25, 34,  3, 35,  8, 29, 36, 21,
        1, 16, 14,  4,  5, 15, 10,  0, 37, 40])

>>> rng.permutation(4)

array([0, 1, 2, 3])

>>> rng.permutation(3)

array([1, 0, 2])

>>> rng.permutation(3)

array([2, 0, 1])

```

And I still build the hashmap before:

```python

idx.get_loc(keys[0])

```

Here are the results:

![measure2.png](../asset/common_files/Matplotlib/measure2.png)

We see that it quite matches the part under `n = 1_000_000` from the last benchmark.

We still see a slight increase over the `n` size but nothing dramatic as the last one, it's mostly due to **latency increasing for the average key value requested (because hashmap too large to fit the L1 / L2 / L3 cache for example -> then "hot" keys)**.

So the questions `pandas` dev asked are probably:

- "At which moment should we start using the binary search tree when possible ?"

- "From which point does the construction cost of a hashmapis probably not amortized anymore by the search themself ?"

The answer `n = 1_000_000` is a strong but reasonable asumption.

I mean technically if we do A LOT of lookups in the `pd.Index`, even the construction cost when `n = 2_000_000` is amortized.

Because what I did not show you for now is the `elapsed` time with the hashmap construction cost taken into account in both logic:

```python

import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys1 = []
ys2 = []

n_repeats = 10_000

rng = np.random.default_rng(55)

for n in xs:

    steps = rng.integers(1, 5, size = n)

    idx = pd.Index(np.cumsum(steps))
    keys = rng.choice(idx.to_numpy(), size = n_repeats)

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys1.append(elapsed / n_repeats)

for n in xs:
    
    idx = pd.Index(rng.permutation(n))
    keys = np.random.randint(0, n, size = n_repeats)

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys2.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys1, "r*-", label = "Monotonic Index")
ax.plot(xs, ys2, "b*-", label = "Shuffled index")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")
ax.legend()

fig.savefig("measure0b.png")


```

![measure0b.png](../asset/common_files/Matplotlib/measure0b.png)

For the red curve, the "jump" arround `n = 1_000_000` is not so dramatic lol, normal there is no jump because it peaked before due to the increasing cost of the hashmap construction.

And we can now tell why `pandas` dev have chosen this value of `n` to switch to a binary search when possible, because that's arround where the binary search is becomes a serious performance improovment. 

I have also extended to `n = 5_000_000` to better see the increasing performance difference.

But again, this is just the **average for one lookup**, so if you still need to perform A LOT of lookups on the `Index`, a hashmap could be the serious improovment.

And if your `Index` values are sorted, so the manual construction of a hashmap like we did before can be beneficial.

Again: "From how many lookups does the hashmap creation cost is amortized ?"

Finally, I want to perform the same benchmark with non-unique keys:

```python

import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = [[]] * (25 - 3)

n_repeats = 10

rng = np.random.default_rng(55)

DISTINCT_INDICES = rng.permutation(np.arange(3, 25))

for CNT in range(0, 25 - 3, 1):

    DISTINCT_INDEX = DISTINCT_INDICES[CNT]

    for n in xs:
    
        hmn1 = n // DISTINCT_INDEX
        counts = np.full(DISTINCT_INDEX,
                         hmn1, 
                         dtype = np.int32)
        counts[: n % DISTINCT_INDEX] += 1
        steps = rng.permutation(np.arange(DISTINCT_INDEX))
        idx = pd.Index(np.repeat(steps, counts))
    
        keys = rng.choice(steps, size = n_repeats)
    
        idx.get_loc(keys[0])
    
        start = time.perf_counter()
    
        for key in keys:
            idx.get_loc(key)
    
        elapsed = time.perf_counter() - start
    
        ys[CNT] = np.append(ys[CNT], (elapsed / n_repeats))

fig, ax = plt.subplots()

vls = np.linspace(0, 1, (25 - 3))

reds = vls

greens = vls
greens = np.roll(greens, len(greens) // 2)

blues = vls

#colors = plt.colormaps["turbo"]( np.linspace(0, 1, (25 - 3)) )

for i in range(0, 25 - 3, 1):
    ax.plot(xs, 
            ys[i], 
            marker = "*", 
            linestyle = "-",
            color = (reds[i], greens[i], blues[i]),
            label = f"{DISTINCT_INDICES[i]}")

ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")
ax.legend()

fig.savefig("measure5.png")


```

Here are the results:

![measure5.png](../asset/common_files/Matplotlib/measure5.png)

We observe that there is no performance difference related to the number of dupplicates, normal the same search algo is performed.

Also, I put that benchmark to show you a subtelty that I camme accross when benchmarking that led me to the opposie conclusion.

If I didn't write:

```python

DISTINCT_INDICES = rng.permutation(np.arange(3, 25))

```

But instead:

```python

DISTINCT_INDICES = np.arange(3, 25)

```

I would have this result:

![measure5b.png](../asset/common_files/Matplotlib/measure5b.png)

We clearly see that the `pd.Index` that have more distinct values have a lower executin time, but this is just a benchmark artifact due to the CPU being on "turbo" the more the programm runs and because the we have a number of distinct values that increases then the `pd.Index` that are ran at the end (more distinc values) are those that takes advantage of the CPU "turbo" mode.

Then when I do the following:

```python

DISTINCT_INDICES = np.arange(3, 25)[::-1]

```

I have the opposite results:

![measure5c.png](../asset/common_files/Matplotlib/measure5c.png)

But wait, because I generated keys as:

```python

steps = rng.permutation(np.arange(DISTINCT_INDEX))
idx = pd.Index(np.repeat(steps, counts))

```

`.idx_loc()` can take advantage of this block representation and may return a `slice()`, then I have to make it really shuffled, unordered is not sufficient.

So I update the key generation to:

```python

steps = rng.integers(0, DISTINCT_INDEX, size = n)
idx = pd.Index(steps)

```

To make the return type a boolean array.

And now I have:

![measure5d.png](../asset/common_files/Matplotlib/measure5d.png)

Which leads to the same conclusion, but we see that on average, the execution time is 2 times higher.

But it was all a lie !

Yess, `.get_loc` only return a slice when the keys values are contiguous AND monotonic:

```python

>>> x = pd.Index([2, 2, 1, 1, 1, 3, 3] + list(np.full(45, 7))) # contiguous non-monotonic

>>> x.get_loc(7)
array([False, False, False, False, False, False, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True])

>>> x2 = pd.Index(np.repeat(list(range(5)), np.full(5, 12))) # contiguous AND monotonic

>>> x2.get_loc(2)
slice(24, 36, None)

```

So, yess the liearly increasing `elapsed_time` aspect of the last 2 benchmarks is explained by the simple fact that the more `n` grows, the more we need to allocate for the returned boolean vector.

But then, why this 2X difference between the last 2 benchmarks ?

The performance difference is mainly due to the fact that the contiguous same-value keys `pd.Index` has much better cache-locality than the fully shuffled key values `pd.Index`, again just low-level principles.

And for a monotonic non-unique `pd.Index` it can use the `np.searchsorted()` path which led to performance improovements.

But what is `searchsorted()` ?

It's just the function that returns the first (`side = "left"`) or last (`side = "right"`) index of a value in an array:

```python

>>> np.searchsorted(np.repeat(np.array(list(range(4))), np.full(4, 5)), 3, side="left")
np.int64(15)

>>> np.searchsorted(np.repeat(np.array(list(range(4))), np.full(4, 5)), 3, side="right")
np.int64(20)

```

Then, it just make a slice of it from the lower and upper bound.

So, to make a monotonic non-unique `pd.Index`, I do:

```python


hmn1 = n // DISTINCT_INDEX
counts = np.full(DISTINCT_INDEX,
                 hmn1, 
                 dtype = np.int32)
counts[: n % DISTINCT_INDEX] += 1
steps = np.arange(DISTINCT_INDEX)
idx = pd.Index(np.repeat(steps, counts))

```

And I benchmark `.get_loc()`.

Here are the results:

![measure5e.png](../asset/common_files/Matplotlib/measure5e.png)

As you see it's very efficient because it's not forced to allocate for a n size boolean vector.

The contract to do that is:

- contiguous key values

- monotonicly increasing 

This is true for all `Index` variants, so no surprise if I restate it a bit differently in the next parts.

Leaving the wrapping logic and going back to default the implementation semantic.

If we have the same key multiple times, it returns a **boolean numpy array** (`.iloc[]` can also consume it).

```python

x = pd.Index(["julien", "antoine", "lucas", "baptiste", "antoine"])
print(x.get_loc("antoine"))

```

Output.

```

array([False,  True, False, False,  True])

```

If the dupplicated keys are contiguous, it returns a `slice` (that `.iloc[]` can also consume):

```python

>>> x
1     A
3     C
3     D
4     E
5     F
10    B
dtype: str

>>> x.index.get_loc(3)
slice(1, 3, None)

```

When it's not contiguous anymore, it returns a boolean numpy array as we saw it:

```python

>>> x2 = pd.concat([x, pd.Series("S", index = [3])], axis = 0)

>>> x2.index.get_loc(3)

array([False,  True,  True, False, False, False,  True])

```

Because `get_loc`' s output differe regarding dupplication and contiguousness (scalar, boolean vector, slice):

```python

>>> x.index.get_loc(1)
0

>>> x.index.get_loc(3)
array([ False, True,  True, False,  False, False ])

```

If you want a predictable output (boolean vector), do the comparisons, it's vectorized:
 
```python

>>> x.index == 3
array([ False, True,  True, False,  False, False ])

```

We also have the `.get_indexer()` method, that is like a `.get_loc()` but for multiple values.

Example:

```python

import pandas as pd

idx = pd.Index(["a", "b", "c"])

idx.get_indexer(["c", "a", "x"])

```

Output.

```

array([2, 0, -1])

```

Note, `-1` means no present.

Also, note that `.get_indexer()` only works on `pd.Index` that have unique values:

```python

>>> x2 = pd.Index( np.random.permutation(np.repeat(list(range(7)), np.full(7, 3))) )

>>> x2.get_indexer([1])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/base.py", line 3728, in get_indexer
    raise InvalidIndexError(self._requires_unique_msg)
pandas.errors.InvalidIndexError: Reindexing only valid with uniquely valued Index objects

```

Therefore, when we have a `pd.Index` that may have dupplicated values, we use `.get_indexer_for()` method:

```python

>>> x2 = pd.Index( np.random.permutation(np.repeat(list(range(7)), np.full(7, 3))) )
>>> x2.get_indexer_for([1])
array([ 0,  3, 14])

```

Then, I want to make a benchmark using `.get_indexer_for()` on a `pd.Index` with non unique keys.

It should be faster than `.get_loc` for `pd.Index` with non-unique keys because this just return a compact array with only the position of the queried key.

Indeed, for a sufficiently high number of unique keys, the occurence of the keys are low.

And we also know that a boolean can be encoded onto only 1 byte.

While the integers returned by `.get_indexer_for()` are 8 bytes integers (64 bits):

```python

Index([0, 1, 1, 6, 0, 2, 6, 4, 4, 0, 2, 3, 4, 1, 5, 5, 3, 6, 5, 2, 3], dtype='int64')
>>> x2.get_indexer_for([3])[0]
np.int64(11)

```

So the memory advantage of `.get_indexer_for` is at first glance when:

```

8k < n

```

`n` being the length of the `pd.Index` and `k` the average occurence of a key.

So let's test this hypothesis:

```python

import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 3_000_000, 100_000))
ys = [[]] * (25 - 3)

n_repeats = 10

rng = np.random.default_rng(55)

DISTINCT_INDICES = rng.permutation(np.arange(3, 25))

for CNT in range(0, 25 - 3, 1):

    DISTINCT_INDEX = DISTINCT_INDICES[CNT]

    print(f"--- CNT : {CNT} / {25 - 3} ---")

    for n in xs:
    
        print(f"n : {n}")

        steps = rng.integers(0, DISTINCT_INDEX, size = n)
        idx = pd.Index(steps)
    
        keys = rng.choice(steps, size = n_repeats)
    
        idx.get_indexer_for([keys[0]])
    
        start = time.perf_counter()
    
        for key in keys:
            idx.get_indexer_non_unique([ key ])
    
        elapsed = time.perf_counter() - start
    
        ys[CNT] = np.append(ys[CNT], (elapsed / n_repeats))

fig, ax = plt.subplots()

vls = np.linspace(0, 1, (25 - 3))

reds = vls

greens = vls
greens = np.roll(greens, len(greens) // 2)

blues = vls

#colors = plt.colormaps["turbo"]( np.linspace(0, 1, (25 - 3)) )

for i in range(0, 25 - 3, 1):
    ax.plot(xs, 
            ys[i], 
            marker = "*", 
            linestyle = "-",
            color = (reds[i], greens[i], blues[i]),
            label = f"{DISTINCT_INDICES[i]}")

ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")
ax.legend()

fig.savefig("measure6b.png")


```

Note that `.get_indexer_non_unique()` is the method `.get_indexer_for()` is dispatched to when the `Index` has not only unique values.

Here are the results:

![measure6b.png](../asset/common_files/Matplotlib/measure6b.png)

Ouch, not what I intended !

For retrieving all occurrences of one label, `.get_indexer_for()` is an unnecessarily general abstraction: it routes the operation through non-unique alignment machinery instead of using the simpler scalar-lookup result produced by `get_loc()`. 

Consequently, converting the Boolean mask returned by `.get_loc()` with `np.flatnonzero()` can be considerably faster than calling `.get_indexer_for([key])`, especially if we search for just one key.

Let's proove it:

```python

import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 3_000_000, 100_000))
ys = [[]] * (25 - 3)

n_repeats = 10

rng = np.random.default_rng(55)

DISTINCT_INDICES = rng.permutation(np.arange(3, 25))

for CNT in range(0, 25 - 3, 1):

    DISTINCT_INDEX = DISTINCT_INDICES[CNT]

    print(f"--- CNT : {CNT} / {25 - 3} ---")

    for n in xs:
    
        print(f"n : {n}")

        steps = rng.integers(0, DISTINCT_INDEX, size = n)
        idx = pd.Index(steps)
    
        keys = rng.choice(steps, size = n_repeats)

        idx.get_loc(keys[0])
    
        start = time.perf_counter()
    
        for key in keys:
            np.flatnonzero(idx.get_loc(key))
    
        elapsed = time.perf_counter() - start
    
        ys[CNT] = np.append(ys[CNT], (elapsed / n_repeats))

fig, ax = plt.subplots()

vls = np.linspace(0, 1, (25 - 3))

reds = vls

greens = vls
greens = np.roll(greens, len(greens) // 2)

blues = vls

#colors = plt.colormaps["turbo"]( np.linspace(0, 1, (25 - 3)) )

for i in range(0, 25 - 3, 1):
    ax.plot(xs, 
            ys[i], 
            marker = "*", 
            linestyle = "-",
            color = (reds[i], greens[i], blues[i]),
            label = f"{DISTINCT_INDICES[i]}")

ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")
ax.legend()

fig.savefig("measure6c.png")

```

Here are the results:

![measure6c.png](../asset/common_files/Matplotlib/measure6c.png)

That's intended.

And even for searching multiple keys once as the `.get_indexer_for()` API was designed to provide, so I re-execute the benchmark but updated the search part to:

```python

for key1, key2 in zip(keys[::2], keys[1::2]):
    np.append(
              np.flatnonzero(idx.get_loc(key1)),  
              np.flatnonzero(idx.get_loc(key2))
             )

```

To have the positions of 2 keys in one iteration.

Here are the results:

![measure6d.png](../asset/common_files/Matplotlib/measure6d.png)

Almost no difference from the previous benchmark, that's why `.get_loc()` + `np.flatnonzero()` is better and should replace `.get_indexer_for()` imo.

In fact a convenient use of `.get_indexer_for()` is when you want to search for target values in a source according to the order of target:

```python

>>> x1 = pd.Index(list("abcde"))

>>> x2 = pd.Index(list("ace"))

>>> x1[x1.get_indexer_for(x2)]

Index(['a', 'c', 'e'], dtype='str')

```

Also, this is a very inefficient method to construct a `numpy.ndarray` that is continuously increasing from `0` to the length of `Index` is:

```python

ser.index.get_indexer(ser.index)

```

Output.

```

array([0, 1, 2, 3, 4, 5])

```

But, for the same thing we can just do:

```python

np.array(range(0, ser.size))

# OR

np.arange(0, ser.size)

```

Or with the `.count()` method.

```python

np.array(range(0, ser.count()))

```

You also see that `.size` attribute and `.count()` method are shared accross most of `pandas` own datatypes. 

Quick remainder: `.size` returns the object's number of elements while `.count` returns the object's number of non `None` elements:

```python

>>> pd.Series([1, 2, None, 3]).size
4

>>> pd.Series([1, 2, None, 3]).count()
np.int64(3)

```

`pd.Index` also have the `.values` attribute, it contains its sorted underlying values as a `numpy.ndarray`

```python

>>> x.index
Index([1, 3, 3, 4, 5, 10], dtype='int64')

>>> x.index.values
array([ 1,  3,  3,  4,  5, 10])

```

Note: For newer versions, we recommend to use `.array` attribute instead of `.values` attribute.

```python

>>> pd.Index([1, 2, 3]).values
array([1, 2, 3])

>>> pd.Index([1, 2, 3]).array
<NumpyExtensionArray>
[1, 2, 3]

```

`NumpyExtensionArray` is a `pandas` interface allowing tocall pandas method on it in addition to `numpy` methods even if the underlying storage is normal `numpy.ndarray`.

If we want pure `numpy.ndarray`, we use `.to_numpy()`:

```python

>>> pd.Index([1, 2, 3]).to_numpy()
array([1, 2, 3])

>>> type(pd.Index([1, 2, 3]).to_numpy())
<class 'numpy.ndarray'>

```

But here we could not use `pandas` method `.isna()` for example:

```python

>>> pd.Index([1, 2, 3]).to_numpy.isna()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'function' object has no attribute 'isna'

```

While this works:

```python

>>> pd.Index([1, 2, 3]).array.isna()
array([False, False, False])

```

You can also replace `index` values with the `.where()` method:

```python

>>> x = pd.Index(list(range(0, 10)))

>>> x.where(x != 2, other = 22)
Index([0, 1, 22, 3, 4, 5, 6, 7, 8, 9], dtype='int64')

```

The logic is; "keep all elements that respects the condition, and **replace** the rest with `other` value.

And I write **replace** for a reason, because even if you replace it with a function thinking it would apply it on the related element, it does not but replace the element with the function:

```python

>>> pd.Index(list(range(0, 10, 1))).where([False] * 10, other = lambda x: x * 2)
Index([<function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>,
       <function <lambda> at 0x76c8fab0a340>],
      dtype='object')

```

This makes no sense here because all elements are the same lambda, but for the sake of it here what we can do:

```python

>>> x[1](2)
4

```

Then, we can map all the functions to a monotonicly increasing value for example:

```python

>>> [f(i) for i, f in enumerate(x)]
[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

```

This is a shared method accross `Index` types.

But, as you get it, for applying a function over elements we can't use `.where()`, we use `.map`.

```python

>>> pd.Index(list(range(0, 10, 1))).map(lambda x: x *2)
Index([0, 2, 4, 6, 8, 10, 12, 14, 16, 18], dtype='int64

```

It works for all `Index` types:

```python

>>> pd.TimedeltaIndex([pd.Timedelta(days = i) for i in range(0, 10, 1) ]).map(lambda x: x *2)

TimedeltaIndex([ '0 days',  '2 days',  '4 days',  '6 days',  '8 days',
                '10 days', '12 days', '14 days', '16 days', '18 days'],
               dtype='timedelta64[us]', freq=None)

>>> pd.TimedeltaIndex([ ( pd.Timestamp(f"2024-01-{i:02d}") - pd.Timestamp("1970-01-01") ) for i in range(1, 12, 1) ])

TimedeltaIndex(['19723 days', '19724 days', '19725 days', '19726 days',
                '19727 days', '19728 days', '19729 days', '19730 days',
                '19731 days', '19732 days', '19733 days'],
               dtype='timedelta64[us]', freq=None)

```

Small note on string integer formating.

The `"{i:02d}"` is essential to format the day placeholder of the date because it must be encoded over 2 characters and padded with `"0"`:

Its synthax is `PADDINGCAHR` followed by `MINIMUMSTRINGLENGTH` and then the representation type (here integer so `d`), bu default padding character is just a space:

```python

>>> f2 = lambda x: print(f"{x:7d}")

>>> f2(-1)
     -1

>>> f2(1)
      1

```

But of course we can choose it:

```python

>>> f2 = lambda x: print(f"{x:07d}")

>>> f2(1)
0000001

>>> f2(-1)
-000001

```

Here the sign if the integer is before the padding.

But we can precise the padding method used.

By default, it is right-aligned:

```python

>>> f2 = lambda x: print(f"{x:7d}")

>>> f2(-1)
     -1

>>> f2(1)
      1

```

When I still do no declare the padding method used, I semantically can only use the `"0"` or default empty space padding character because otherwise it is interpreted as the padding method, here's why:

- Right-laigned (explicit)

```python

>>> f2 = lambda x: print(f"{x:*>7d}")

>>> f2(-1)
*****-1

>>> f2(1)
******1

```

- Left-aligned

```python

>>> f2 = lambda x: print(f"{x:*<7d}")

>>> f2(1)
1******

>>> f2(-1)
-1*****

```

- Middle-aligned

```python

>>> f2 = lambda x: print(f"{x:*^7d}")

>>> f2(-1)
**-1***

>>> f2(1)
***1***

```

You also can choose to always show the sign with delcaring `"+"` after the padding method:

```python

>>> f2 = lambda x: print(f"{x:*>+7d}")

>>> f2(-1)
*****-1

>>> f2(1)
*****+1

```

`"="` is also its own padding method, it's like left padding but the sign is displayed before the padded character(s) (with no `"+"` set it's then only different from `">"` for negative integers).

```python

>>> f2 = lambda x: print(f"{x:0=7d}")

>>> f2(1)
0000001

>>> f2(-1)
-000001

```

So:

```python

>>> f2 = lambda x: print(f"{x:0=+7d}")

>>> f2(-1)
-000001

>>> f2(1)
+000001

```

There is also a convention when we have for example:

```

"07d"

```

(`7` is randomly chosen for the example here)

Then we think it's equivalent to:

```

"0>7d"

```

Because of the default padding method normally being `">"`, but no, that's equivalent to:

```

"0=7d"

```

Look:

```python

>>> f2 = lambda x: print(f"{x:07d}")

>>> f2(1)
0000001

>>> f2(-1)
-000001

```

Annnnnd, there are mutiple types of `pd.Index`:

```

pd.Index              # generic/base index
pd.RangeIndex         # compact integer range: start/stop/step
pd.CategoricalIndex   # index backed by Categorical codes/categories
pd.MultiIndex         # hierarchical / tuple-like index
pd.IntervalIndex      # index of intervals
pd.DatetimeIndex      # datetime64-based index
pd.TimedeltaIndex     # timedelta64-based index
pd.PeriodIndex        # period/time-span index

```

There's still some methods belonging to `pd.Index` that I did not discuss yet, but because they are shared accross all `Index` variants I will discuss them all along the explanation of those variants.


### `pd.RangeIndex`

That's the one we implicitely worked with.

For example, default `pd.DataFrame` and `pd.Series` comes with this one as their `index`.

It does not store `index` as a huge numpy array (`numpy.ndarray`), but instead as a `Range(start, stop, step)` (a bit like `ALTREP` format in `R`)

Then, wen you define a `Series`, use `RangeIndex`:

```python

pd.Series([1,2,3,4,5], 
          index=pd.RangeIndex(1, 6, 1))

```

Output.

```

1    1
2    2
3    3
4    4
5    5
dtype: int64

```

```

print(df.index)

```

Output.

```

RangeIndex(start=0, stop=100000, step=1)

```

When we don't precise the `Index` type, it defaults to `RangeIndex`:

```python

>>> pd.Series([1, 2, 3, 4, 5]).index
RangeIndex(start=0, stop=5, step=1)

```

So when random accessing some data to get its position with `.get_loc()` , it does something like that:

```

def get_loc_range_index(key, start, stop, step):
    # first: check key is inside the valid range
    if step > 0:
        if key < start or key >= stop:
            raise KeyError(key)
    else:
        if key > start or key <= stop:
            raise KeyError(key)

    # second: check key lands exactly on the step grid
    diff = key - start
    if diff % step != 0:
        raise KeyError(key)

    # third: convert label -> physical integer position
    return diff // step

```

No need for creating and maintaining a hashmap neither a binary tree !

Now, let's take a look at its performance:

```python

import pandas as pd
import matplotlib.pyplot as plt
import random
import time

xs = list(range(1_000, 2_000_000, 100_000))
ys = []

n_repeats = 10_000

for n in xs:
    idx = pd.RangeIndex(range(n))
    keys = [random.randint(0, n - 1) for _ in range(n_repeats)]

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure_range_index.png")

```

Note that here a more performant method to generate random integer from a lower to an upper bound is to use the vectorized equivalent:

```python

keys = np.random.randint(low = 0, 
                         high = n, 
                         size = n_repeats)

```

(Here, the upper bound is exclusive, so we put `n`)

(Also, `low` and `high` argument is more speaking than respectively `a` and `b` for `random.randint()`)

!![measure_range_index.png](../../assets/common_files/Matplotlib/measure_range_index.png)

It is pretty constant, the variations are due to noise (wa are at an order of magnitude where noise has a strong impact).

Compared to the binary and hashmap search mechanism from `pd.Index`, it's clearly the fastest, especially if inclusing the hashmap construction cost.

Back to usage.

You can apply slices on your `RangeIndex` object.

```python

print(ser.index[::-1])

```

Output.

```

RangeIndex(start=5, stop=-1, step=-1)

```

Here are some methods `Index` have:

```

idx.equals(other)
idx.intersection(other)
idx.union(other)
idx.difference(other)
idx.symmetric_difference(other)
idx.get_indexer(other)
idx.is_unique
idx.is_monotonic_increasing

```

Of course `RangeIndex` is only used when the `index` values are monotonicly increasing / decreasing.

And, when the step is a constant integer.

You can check `.is_monotonic_increasing`.

```python

>>> pd.RangeIndex(10, 0, -1).is_monotonic_increasing
False
>>> pd.RangeIndex(0, 10, 1).is_monotonic_increasing
True

```

A note about the difference between `.difference` and `.symmetric_difference()`.

`.symmetric_difference()` is straight forward:

```python

>>> idx1
Index([2, 0, 1], dtype='int64')
>>> idx2
RangeIndex(start=0, stop=6, step=1)
>>> idx1.symmetric_difference(idx2)
Index([3, 4, 5], dtype='int64')

```

Elements that are in one or the other set but not in both.

BUT `.difference()` method is like elements that are in the first set (Index from which the method is called) but not in the second one.

```python

>>> idx1.difference(idx2)
Index([], dtype='int64')

```

```python

>>> idx2.difference(idx1)
RangeIndex(start=3, stop=6, step=1)

```

You saw that when the result is monotonicly increasing (**and the step being a constant integer**), it is directly converted to a `RangeIndex`.

`Index` can be used as column in a `DataFrame`, but they are automatically converted to `pd.Series`.

Here, we'll use `pd.date_range()` method that returns a `pd.DatetimeIndex`, more on this one here: [pd.DatetimeIndex](#`pd.DatetimeIndex`)

```python

>>> x = pd.date_range("2024-01-01", periods = 15, freq="D")

>>> type(x)
<class 'pandas.DatetimeIndex'> # see later

>>> df = pd.DataFrame({ 
            "timestamp": x, 
            "day": x.strftime("%Y-%m-%d"), 
            "col3": pd.RangeIndex(0, 15, 1)}
)

>>> df
                   timestamp         day  col3
0  2024-01-16 00:10:00+01:00  2024-01-16     0
1  2024-01-23 00:10:00+01:00  2024-01-23     1
2  2024-01-30 00:10:00+01:00  2024-01-30     2
3  2024-02-06 00:10:00+01:00  2024-02-06     3
4  2024-02-13 00:10:00+01:00  2024-02-13     4
5  2024-02-20 00:10:00+01:00  2024-02-20     5
6  2024-02-27 00:10:00+01:00  2024-02-27     6
7  2024-03-05 00:10:00+01:00  2024-03-05     7
8  2024-03-12 00:10:00+01:00  2024-03-12     8
9  2024-03-19 00:10:00+01:00  2024-03-19     9
10 2024-03-26 00:10:00+01:00  2024-03-26    10
11 2024-04-02 00:10:00+02:00  2024-04-02    11
12 2024-04-09 00:10:00+02:00  2024-04-09    12
13 2024-04-16 00:10:00+02:00  2024-04-16    13
14 2024-04-23 00:10:00+02:00  2024-04-23    14

>>> type(df["day"])
<class 'pandas.Series'>

>>> type(df["timestamp"])
<class 'pandas.Series'>

>>> type(df["col3"])
<class 'pandas.Series'>

```

Therefore, here the `pd.RangeIndex` variable can be seen as a lazy variable that is extended/computed when needed.

Also, the `.take` method may return an `.Index` if the subrange can not be infered as a `pd.RangeIndex`:

```python

>>> pd.RangeIndex(0, 10, 1).take([1, 3, 4])
Index([1, 3, 4], dtype='int64')

```

Because in the example above, the step is not constant.

But here it is, so the semantic type is respected:

```python

>>> pd.RangeIndex(0, 10, 1).take(list(range(2, 6)))
RangeIndex(start=2, stop=6, step=1)

```

`.take` is a shared method accross all `Index` variant, and it returns the same semantic type than the `Index` it's applied on when it can (basically for al types apart from `pd.RangeIndex` when its properties can't repected).

We have the same concept for `.where` for example:

```python

>>> pd.RangeIndex(0, 10, 1).where(x != 2, other = 22)
Index([0, 1, 22, 3, 4, 5, 6, 7, 8, 9], dtype='int64')

```

### `pd.CategoricalIndex()`

When you want to labelize your data with categorical values **as the index**.

```python

>>> pd.Series([0,1,2,3,4,5], index=pd.CategoricalIndex(["small", "medium", "large"] * 2))
small     0
medium    1
large     2
small     3
medium    4
large     5
dtype: int64

```

Here are the methods related to `pd.CategoricalIndex()`.

```

idx.categories                 # category labels
idx.codes                      # integer codes
idx.ordered                    # whether order matters
idx.rename_categories(...)     # rename category labels
idx.reorder_categories(...)    # change category order
idx.add_categories(...)        # add allowed categories
idx.remove_categories(...)     # remove categories, values become NaN
idx.remove_unused_categories() # cleanup unused categories (that are not in current data)
idx.set_categories(...)        # add/remove/reorder in one call
idx.as_ordered()               # make ordered
idx.as_unordered()             # make unordered
idx.map(...)                   # map labels

```

Also, when you create a categorical index, you can specify the possible set of categories.

```python

x = pd.Series([1,2,3,4], 
             index=pd.CategoricalIndex(
                            ["A", "A", "B", "A"], 
                            categories=["B", "A", "C"], 
                            ordered=True)
)

```

You see that `categories` option specify all the possible categories, but also the **sort order**.

Then.

```python

>>> x.index.sort_values()
CategoricalIndex(['B', 'A', 'A', 'A'], categories=['B', 'A', 'C'], ordered=True, dtype='category')

```

`ordered=True` has nothing to do with the sort order of the values by their keys relatively to the order of the categories in `categories`.

```python

>>> x = pd.Series([1,2,3,4], index=pd.CategoricalIndex(["A", "A", "B", "A"], categories=["A", "B", "C"], ordered=False))
>>> x.index.sort_values()

CategoricalIndex(['A', 'A', 'A', 'B'], categories=['A', 'B', 'C'], ordered=False, dtype='category')

>>> x = pd.Series([1,2,3,4], index=pd.CategoricalIndex(["A", "A", "B", "A"], categories=["A", "B", "C"], ordered=True))
>>> x.index.sort_values()

CategoricalIndex(['A', 'A', 'A', 'B'], categories=['A', 'B', 'C'], ordered=True, dtype='category')

>>> x = pd.Series([1,2,3,4], index=pd.CategoricalIndex(["A", "A", "B", "A"], categories=["B", "A", "C"], ordered=True))
>>> x.index.sort_values()

CategoricalIndex(['B', 'A', 'A', 'A'], categories=['B', 'A', 'C'], ordered=True, dtype='category')

>>> x = pd.Series([1,2,3,4], index=pd.CategoricalIndex(["A", "A", "B", "A"], categories=["B", "A", "C"], ordered=False))
>>> x.index.sort_values()

CategoricalIndex(['B', 'A', 'A', 'A'], categories=['B', 'A', 'C'], ordered=False, dtype='category')

```

But it defines if categories can be relationaly comparable.

If I set `ordered=False`, I can not even compare to a category that belongs to the set of possible categories.

```python

>>> x = pd.Series([1,2,3,4], 
                  index=pd.CategoricalIndex(["A", "A", "B", "A"], 
                                            categories=["A", "B", "C"], 
                                            ordered=False)
)
>>> x.index < "B"

```

--> Error

But setting it to `True`.

```python

>>> x = pd.Series([1,2,3,4], 
                  index=pd.CategoricalIndex(["A", "A", "B", "A"], 
                                            categories=["A", "B", "C"], 
                                            ordered=True)
)
>>> x.index < "B"
array([ True,  True, False,  True])

```

You can check if an element belongs to the set of categories.

```python

>>> "B" in x.index
True

```

Is In ?

```python

>>> x.index.isin(["A", "B"])
array([ True,  True,  True,  True])

```

The `codes` attribute, map each element to the index of the category.

```python

>>> x.index.codes
array([0, 0, 1, 0], dtype=int8)

```

All elements are `"A"` apart fom the third one which satisfies `x.index.values[x.index.codes[2]] == "B"`

And yes, as suggested before `Index` have their `.values/array` attributes:

```python

>>> x.index.values

['A', 'A', 'B', 'A']
Categories (3, str): ['A' < 'B' < 'C']

```

Ho a new type appeared !

What is `Categories`' type' ?

```python

>>> type(pd.CategoricalIndex([1, 2, 3]).values)
<class 'pandas.Categorical'>

```

A `pd.Categorical` is a necessary abstraction object for storing codes related to categories, enabling comparisons when `ordered = True`, asserting the finite set of categories with `categories`.

Also, attributes access like:

```python

>>> pd.CategoricalIndex(list("ABC")).categories
Index(['A', 'B', 'C'], dtype='str')

>>> pd.CategoricalIndex(list("ABC")).codes
array([0, 1, 2], dtype=int8)

```

Are respectively forwarded to the underlying `pd.Categorical` as:

```python

>>> pd.CategoricalIndex(list("ABC")).values.codes
array([0, 1, 2], dtype=int8)

>>> pd.CategoricalIndex(list("ABC")).values.categories
Index(['A', 'B', 'C'], dtype='str')

```

Also, note that the `.codes` default values is determined by lexicographically sorting the categories values:

```python

>>> ser = pd.Series([1, 2, 2, 3], 
                    index = pd.CategoricalIndex(["small", "medium", "medium", "large"], ordered = True))

>>> ser.index.categories
Index(['large', 'medium', 'small'], dtype='str')

>>> ser.index.codes
array([2, 1, 1, 0], dtype=int8)

```

The `.codes` attribute is fundamental, because it allow the search mechanism to work approximately the same as for standard `pd.Index`.

For `x.index.get_loc(X)` for example, it conceptually does:

```python

>>> x = pd.Series([1, 2, 3] * 3, 
            index = pd.CategoricalIndex(["small", "medium", "large"] * 3)
        )

>>> cat_code = x.index.categories.get_loc("medium")

>>> positions = locate_code(x.index.codes, cat_code)

```

The first phase is:

```python

>>> cat_code = x.index.categories.get_loc("medium")

```

`x.index.categories` is itself a `pd.Index`. 

So it performs the same machinery to get the related category code.

And once it has it, we can begin the second phase:

```python

positions = locate_code(x.index.codes, cat_code)

```

Where `locate_code` is not a real function, just a placeholder to describe the mechanism used for querying the positions.

So it can be binary search if the codes are sorted like so:

```python

>>> ser = pd.Series([1, 2, 2, 3], 
                    index = pd.CategoricalIndex(["small", "medium", "medium", "large"], 
                                                categories = ["small", "medium", "large"]
                                                )
                    )

>>> ser.index.codes
array([0, 1, 1, 2], dtype=int8)

```

Or by maintaining a hashmap and appply the key query on it if not sorted.

So again, if you want to be sure to use a hashmap do the following:

```python

from collections import defaultdict

ser = pd.Series([1, 2, 2, 3], 
                index = pd.CategoricalIndex(["small", "medium", "medium", "large"], 
                                            categories = ["small", "medium", "large"]
                                           )
               )

positions = defaultdict(list)

for position, code in enumerate(ser.index.codes): 
    positions[ser.index.categories[code]].append(position)

```

And use it like:

```python

>>> ser.iloc[positions["medium"]]
medium    2
medium    2
dtype: int64

>>> ser.iloc[positions["large"]]
large    3
dtype: int64

```

Let's benchmark it !

First, a `pd.CategoricalIndex` we can roughly be sure it will use binary search at some point:

```python

import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 10_000

rng = np.random.default_rng(55)

cat_val = (
           "small", 
           "medium", 
           "large", 
           "extra-large"
           )

for n in xs:

    cats = np.array([])

    hmn1 = n // len(cat_val)

    for cv in cat_val:
        cats = np.concatenate( [cats, np.array( [cv] * hmn1 ) ] )

    hmn1 *= len(cat_val)

    if n - hmn1 > 0:
        cats = np.concatenate([ 
                               cats, 
                               cats[:n - hmn1] 
                              ] 
                              )

    idx = pd.CategoricalIndex(cats, categories = cat_val, ordered=True)
    keys = rng.choice(cat_val[:min(n, len(cat_val))], size = n_repeats)

    idx.get_loc(keys[0])

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure_cat_index0.png")


```

Hmm, we can improve the generation of the `pd.CategoricalIndex` from:

```python

cats = np.array([])

hmn1 = n // len(cat_val)

for cv in cat_val:
    cats = np.concatenate( [cats, np.array( [cv] * hmn1 ) ] )

hmn1 *= len(cat_val)

if n - hmn1 > 0:
    cats = np.concatenate([ 
                           cats, 
                           cats[:n - hmn1] 
                          ] 
                          )

idx = pd.CategoricalIndex(cats, categories = cat_val, ordered=True)

```

Which requires allocating `len(cat_val)` arrays for each iteration.

But still I need contiguous blocks of the same key values, so how to do it ?

The `np.repeat()` function is perfectly designed to do that:

```python

>>> import numpy as np

>>> np.repeat(np.array([1, 2, 3]), [2, 3, 3])
array([1, 1, 2, 2, 2, 3, 3, 3])

>>> np.repeat(np.array([1, 2, 3]), [2, 3, 1])
array([1, 1, 2, 2, 2, 3])

>>> np.repeat(np.array(a = [1, 2, 3]), repeats = [1, 3, 3])
array([1, 2, 2, 2, 3, 3, 3])

```

Because here, the underlying implementation directly knows that it must allocate `sum(repeats)`.

So, here is the implementation:

```python

import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 10_000
rng = np.random.default_rng(55)

cat_val = np.array([
    "small",
    "medium",
    "large",
    "extra-large",
])

for n in xs:
    n_categories = len(cat_val)

    counts = np.full(
        n_categories,
        n // n_categories,
        dtype=np.int64,
    )

    counts[: n % n_categories] += 1

    codes = np.repeat(
                np.arange(n_categories, dtype = np.int8),
                counts
            )
    idx = pd.Categorical.from_codes(
                        codes, 
                        categories = cat_val, 
                        ordered = True
           )
    idx = pd.CategoricalIndex(idx)

    keys = rng.choice(cat_val[counts > 0], size=n_repeats)

    idx.get_loc(keys[0])

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start
    ys.append(elapsed / len(keys))

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.tight_layout()
fig.savefig("measure_cat_index1.png")

```

The important part is:

```python

n_categories = len(cat_val)

counts = np.full(
    n_categories,
    n // n_categories,
    dtype=np.int64,
)

counts[: n % n_categories] += 1

codes = np.repeat(
            np.arange(n_categories, dtype = np.int8),
            counts
        )
idx = pd.Categorical.from_codes(
                    codes, 
                    categories = cat_val, 
                    ordered = True
       )
idx = pd.CategoricalIndex(idx)

```

I could have constructed the `pd.CategoricalIndex` as:

```python

cats = np.repeat(cat_val, counts)
idx = pd.CategoricalIndex(
    cats,
    categories=cat_val,
    ordered=True,
)

```

But it would be **less performant because it had to map the codes from the values while the codes are already provided in** `pd.CategoricalIndex(pd.Categorical.from_codes())` constructor.

Therefore, when you have to construct this `Index` type, this is preferable to use this constructor.

And the padding is performed by adding one value block to the firsts categories:

```python

counts[: n % n_categories] += 1

```

Here are the results:

![measure_cat_index1.png](../assets/common_files/Matplotlib/measure_cat_index1.png)

For this monotonic, non-unique `pd.CategoricalIndex`, `.get_loc()` uses duplicate-boundary lookup and returns a slice across the entire tested range. 

It does not change the timed steady-state lookup algorithm, so no large performance discontinuity appears.

For a non-unique monotonic index, pandas’s engine goes to `._get_loc_duplicates()`, which performs two `np.searchsorted` calls and returns a slice:

```python

left  = searchsorted(key, side="left")
right = searchsorted(key, side="right")
return slice(left, right)

```

Now, another benchmark for the unsorted values:

```python

import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 1_000
rng = np.random.default_rng(55)

cat_val = np.array([
    "small",
    "medium",
    "large",
    "extra-large",
])

for n in xs:

    available_codes = np.arange(min(n, len(cat_val)))
    cats = rng.choice(available_codes, size = n)
    idx = pd.Categorical.from_codes(cats, 
                                    categories = cat_val,
                                    ordered = True
                                   )
    idx = pd.CategoricalIndex(idx)

    keys = rng.choice(cat_val[0:len(available_codes)], size=n_repeats)

    idx.get_loc(keys[0])  # warm-up

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start
    ys.append(elapsed / len(keys))

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.tight_layout()
fig.savefig("measure_cat_index2.png")

```

Here are the results:

![measure_cat_index2.png](../assets/common_files/Matplotlib/measure_cat_index2.png)

Woo, why so much higher than the previous one ?

Because of the contiguous nature of the last one, it allowed to return a slice when performing `.get_loc()`:

```python

>>> x
CategoricalIndex(['a', 'a', 'a', 'a', 'a', 'a', 'a', 'b', 'b', 'b', 'b', 'b',
                  'b', 'b', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'd', 'd', 'd',
                  'd', 'd', 'd', 'd', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],
                 categories=['a', 'b', 'c', 'd', 'e'], ordered=False, dtype='category')

>>> x.get_loc("b")
slice(7, 14, None)

```

So no need to allocate for a `n` size boolean array contrary to:

```python

>>> x = pd.CategoricalIndex(np.repeat(np.random.permutation(list("abcde")), np.full(5, 7)), categories = list("abcde"))

>>> x
CategoricalIndex(['a', 'a', 'a', 'a', 'a', 'a', 'a', 'c', 'c', 'c', 'c', 'c',
                  'c', 'c', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'b', 'b', 'b',
                  'b', 'b', 'b', 'b', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
                 categories=['a', 'b', 'c', 'd', 'e'], ordered=False, dtype='category')

>>> x.get_loc("b")
array([False, False, False, False, False, False, False, False, False,
       False, False, False, False, False, False, False, False, False,
       False, False, False,  True,  True,  True,  True,  True,  True,
        True, False, False, False, False, False, False, False])

```

The `elapsed` time is linearly increasing because the returned boolean vector increases over `n`, as simple as that.

By the way, the contact that makes `.get_loc`  returns a slice is not just the contiguousness of the key values, but also the fact that they are monotonicly increasing:

```python

>>> x = pd.CategoricalIndex(pd.Categorical.from_codes([1, 1, 1, 0, 0, 0, 2, 2], categories = list("abc")))

>>> x.get_loc("a")
array([False, False, False,  True,  True,  True, False, False])

>>> x2 = pd.CategoricalIndex(pd.Categorical.from_codes([2, 2, 1, 1, 1, 0, 0, 0], categories = list("abc")))

>>> x2.get_loc("a")
array([False, False, False, False, False,  True,  True,  True])

>>> x3 = pd.CategoricalIndex(pd.Categorical.from_codes([0, 0, 0, 1, 1, 1, 2, 2], categories = list("abc")))

>>> x3.get_loc("a")
slice(0, 3, None)

```

Then, if I had cosntructed the `pd.CategoricalIndex` as:

```python

n_categories = len(cat_val)

counts = np.full(
    n_categories,
    n // n_categories,
    dtype=np.int64,
)

counts[: n % n_categories] += 1

codes = np.repeat(
            rng.permutation(np.arange(n_categories, dtype = np.int8)),
            counts
        )
idx = pd.Categorical.from_codes(
                    codes, 
                    categories = cat_val, 
                    ordered = True
       )
idx = pd.CategoricalIndex(idx)

```

I would have roughly the same results from the shuffled key values benchmark:

![measure_cat_index1b.png](../assets/common_files/Matplotlib/measure_cat_index1b.png)

Back to usage:

Taking / deleting / inserting

Because it is an `Index`:

```python

idx.take([0, 2]) # takes elements by their position -> returns a pd.CategoricalIndex

idx.delete(1) # delete elements by its positon

idx.insert(0, "large") # insert "large" at position 0

```

But insertion must respect categories:

```python

idx.insert(0, "extra_large")

```

will fail unless `"extra_large"` is already a category.

Count occurence of category:

```python

>>> x.index.value_counts()
A    3
B    1
C    0
Name: count, dtype: int64

```

If `ordered=True`, min / max:

```python

>>> x.index.min()
'A'
>>> x.index.max()
'B'

```

Set operations (discussed later in `MultiIndex`):

```python

idx.union(other)
idx.intersection(other)
idx.difference(other)
idx.symmetric_difference(other)

```

Is NA ?

```python

idx.isna()
idx.notna()

```

Missing categorical entries have code `-1`:

Dupplication

```python

>>> x.index.duplicated()
array([False,  True, False,  True])

```

The underlying logic is:

```

"A" first occurrence  -> False
"A" seen again        -> True
"B" first occurrence  -> False
"B" seen again  -> True
"C" unused category   -> no output at all

```

This is also a shared method across `Index` variants:

```python

>>> pd.Index(list(range(0, 10))).duplicated()

array([False, False, False, False, False, False, False, False, False,
       False])

```

Replace category under conditions mask is of course possible through `.where()`:

```python

>>> x.index.where(x.index != "A", other="C")
CategoricalIndex(['C', 'C', 'B', 'C'], categories=['A', 'B', 'C'], ordered=True, dtype='category')

```

Export to numpy. (of course, we can do that with other `Index` Type)

```python

>>> x.index.to_numpy()
array(['A', 'A', 'B', 'A'], dtype=object)

```

For now the index has no name, but of course you can give one in the constructor.

```python

>>> index=pd.CategoricalIndex(
            ["A", "A", "B", "A"], 
            categories=["A", "B", "C"], 
            ordered=True, 
            name="size"
)

```

This works for all `Index` type, it is a usefull metadata to the `Series` that has the index to better describe it, or even when this is the `Index` of a `DataFrame`.

```python

>>> x = pd.Series([1, 2, 3, 4], index = pd.CategoricalIndex(["small", "small", "medium", "small"], categories = ["medium", "small", "large"], ordered = True, name="size"))
>>> x
size
small     1
small     2
medium    3
small     4
dtype: int64

```

And the `name` is of course accessible as an attribute.

```python

>>> x.index.name
'size'

```

To rename category, you can apply a mapping with `.map({...})` method.

`.map()` is usually to apply a function over elements, but it also accepts dict, so it is conceptually transformed as a function with a lookup-table like this:

```python

def dict_mapper(x):

    if x == "Cat1":
        return "Cat1B"
    elif x == "Cat2":
        return "Cat2B"
    else:
        return NaN

```

Example:

```python

>>> x = pd.Series([1, 2, 3, 4], index = pd.CategoricalIndex(["small", "small", "medium", "small"], categories = ["medium", "small", "large"], ordered = True, name="size"))

>>> x.index.map({ "medium": "M", "small": "S", "large": "L" })
CategoricalIndex(['S', 'S', 'M', 'S'], categories=['M', 'S', 'L'], ordered=True, dtype='category', name='size')

```

Note that all categorical values that are represented in the actual data must be present in the dict we are mapping, or it will result in `nan` values for those not pesent.

```pyton

>>> x.index.map({ "medium": "M", "large": "L" })
Index([nan, nan, 'M', nan], dtype='str', name='size')

```

Here, because `"small"` is not present it will be converted to a raw `pd.Index` and will replace `"small"` values by `nan` -> not what you want.

To avoid this, you can use the `.get(x, x)` method of a dictionary, if `x` is found as a key, then it outputs its associated value, if no return `x`:

```python

>>> x.index.map(lambda x: {"medium": "M", "large": "L"}.get(x, x))
CategoricalIndex(['small', 'small', 'M', 'small'], categories=['M', 'small', 'L'], ordered=True, dtype='category', name='size')

```

The logic is:

```python

if x in mapping:
    return mapping[x]
else:
    return x

```

Also, note that `map` is not only appliabe on an `Index`, but also the values of a `Series`:

```python

>>> x = pd.Series([1, 2, 3, 4], index = pd.CategoricalIndex(["small", "small", "medium", "small"], categories = ["medium", "small", "large"], ordered = True, name="size"))

>>> x.map(lambda x: x + 1)
size
small     2
small     3
medium    4
small     5
dtype: int64

# or even on the ndarray

>>> x.array.map(lambda x: x + 1)
array([2, 3, 4, 5])

```

And interestingly, here we begin to see that the old `.values` API has been left over because it does not implement the `.map()` method contrary to `.array`.

```python

>>> x.values.map(lambda x: x + 1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'numpy.ndarray' object has no attribute 'map'. Did you mean: 'max'?

```

Note that when we `.map()` onto a `Series` values/array, the returned array loses its `pandas` wrapper (`NumpyExtensionArray`).

```python

>>> type(x.array)
<class 'pandas.arrays.NumpyExtensionArray'>
>>> type(x.array.map(lambda x: x + 1))
<class 'numpy.ndarray'>

```

To wrap it again, you can use `pd.arrays.NumpyExtensionArray` as follow:

```python

>>> type(pd.arrays.NumpyExtensionArray(x.array.map(lambda x: x + 1)))
<class 'pandas.arrays.NumpyExtensionArray'>

```

You can of course map the category to number and it would return a `CategoricalIndex`, BUT if there are too much category it might fail to return a `CategoricalIndex` and therefore a plain `Index`, so be careful with numbers and use string instead.

```python

>>> x.index.map({"A": 1, "B": 2, "C": 3})
CategoricalIndex([1, 1, 2, 1], categories=[1, 2, 3], ordered=True, dtype='category', name='size')

```

Also note that collapsing category return a plain `Index`.

```python

>>> x.index.map({"A": "a", "B": "c", "C": "c"})
Index(['a', 'a', 'c', 'a'], dtype='str', name='size')

```

Basically, when there is no one to one categorical value matching, then it fallbacks to an `Index`.

If you want to make it a categorical index, just convert it back to one.

```python

>>> pd.CategoricalIndex(x.index.map({"A": "a", "B": "c", "C": "c"}), 
                                    name=x.index.name, 
                                    ordered=x.index.ordered
)
CategoricalIndex(['a', 'a', 'c', 'a'], categories=['a', 'c'], ordered=True, dtype='category', name='size')

```

`categories` attribute is derived from the actual distinct categorical values.

Or even more explicitely.

```python

>>> new_idx = x.index.map({"A": "a", "B": "c", "C": "c"})
>>> pd.CategoricalIndex(new_idx, 
                        name=x.index.name, 
                        ordered=x.index.ordered,
                        categories=new_idx.unique()
)
CategoricalIndex(['a', 'a', 'c', 'a'], categories=['a', 'c'], ordered=True, dtype='category', name='size')

```

An alternative to rename categories that prevents categories collapse (not expansion because it's impossible --> discussed later) is:

```python

>>> x.index.rename_categories(["a", "b", "c"]) # must match the order of x.index.categories
CategoricalIndex(['a', 'a', 'b', 'a'], categories=['a', 'b', 'c'], ordered=True, dtype='category', name='size')

```

We are forced to use this method because we can obviously not set it manually like that:

```python

>>> x.index.categories.array = ["M", "S", "L"]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "pandas/_libs/properties.pyx", line 41, in pandas._libs.properties.CachedProperty.__set__
AttributeError: Can't set attribute

```

If non unique, error:

```python

>>> x.index.rename_categories(["a", "c", "c"])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/extension.py", line 98, in method
    result = attr(self._data, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/categorical.py", line 1265, in rename_categories
    cat._set_categories(new_categories)
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/categorical.py", line 963, in _set_categories
    new_dtype = CategoricalDtype(categories, ordered=self.ordered)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/dtypes/dtypes.py", line 234, in __init__
    self._finalize(categories, ordered, fastpath=False)
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/dtypes/dtypes.py", line 391, in _finalize
    categories = self.validate_categories(categories, fastpath=fastpath)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/dtypes/dtypes.py", line 591, in validate_categories
    raise ValueError("Categorical categories must be unique")
ValueError: Categorical categories must be unique

```

If less category, also erros:

```python

>>> x.index.rename_categories(["a", "b"])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/extension.py", line 98, in method
    result = attr(self._data, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/categorical.py", line 1265, in rename_categories
    cat._set_categories(new_categories)
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/categorical.py", line 969, in _set_categories
    raise ValueError(
ValueError: new categories need to have the same number of items as the old categories!

```

If more, also error:

```python

>>> x.index.rename_categories(["a", "b", "c", "d"])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/extension.py", line 98, in method
    result = attr(self._data, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/categorical.py", line 1265, in rename_categories
    cat._set_categories(new_categories)
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/categorical.py", line 969, in _set_categories
    raise ValueError(
ValueError: new categories need to have the same number of items as the old categories!

```

**It guarantees strict mapping**

More on mapping with categorical index.

At first we could think that we could add new categories (**expansion**) here:

```python

>>> x
size
small     1
small     2
medium    3
small     4
dtype: int64

>>> x.index.map(lambda x: np.random.choice(["A", "B", "C", "D", "E", "F", "G"]))

```

Because we think it applies one per row.

But now in fact it apply **per categorical value present in the data (not even in the possible set of categories)**.

Output.

```python

Index(['C', 'C', 'E', 'C'], dtype='str', name='size')

```

The implementation is conceptually like this:

```python

def categorical_index_map(cat_index, mapper):
    categories = cat_index.categories
    codes = cat_index.codes

    # Map categories, not each row occurrence
    mapped_categories = []

    for cat in categories:
        mapped_categories.append(mapper(cat))

    # Reconstruct the visible index from the old codes
    out = []

    for code in codes:
        if code == -1:
            out.append(np.nan)
        else:
            out.append(mapped_categories[code])

    return pd.Index(out, name=cat_index.name)

```

You can also test this behavior with this code, no need to use `random`.

```python

>>> x2
A    1
B    2
A    1
B    2
A    1
    ..
B    2
A    1
B    2
A    1
B    2
Length: 134, dtype: int64

>>> x2.index

CategoricalIndex(['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B',
                  ...
                  'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
                 categories=['A', 'B'], ordered=False, dtype='category', length=134)

>>> x2.index.map(lambda x: ["A", "B", "C"][int((time.time() * 10000000) % 3)]).unique()

CategoricalIndex(['C', 'B'], categories=['C', 'B'], ordered=False, dtype='category')

```

Expected, it **stores result per categorical value present in the values**.

Remember that all python hashable object can be a category, so this is perfectly valid.

```python

from enum import Enum

class Size(Enum):
    SMALL = 1
    LARGE = 2

pd.CategoricalIndex(
    [Size.SMALL, Size.LARGE, Size.SMALL],
    categories=[Size.SMALL, Size.LARGE]
)

```

### `pd.MultiIndex()`

When you want to make your index as levels for grouping rows.

```python

x = pd.Series([0,1,2,3], 
               index=pd.MultiIndex.from_tuples(
                            [("A", 1), 
                            ("A", 2), 
                            ("B", 1), 
                            ("B", 2)], 
                            name=["group", "number"]))

print(x)

```

Output.

```

group  number
A      1         0
       2         1
B      1         2
       2         3
dtype: int64

```

Just a quick remainder, all `Index` variants are just a container and as its own,  absolutely does not care about relationship with values.

Then the permutation has no effect on the index.

```python

>>> from itertools import product

>>> x = pd.Series([1, 2, 3, 4], index=pd.MultiIndex.from_tuples([(a, b) for a, b in product(["A", "B"], [1, 2])]))

>>> x

A  1    1
   2    2
B  1    3
   2    4
dtype: int64

>>> x.iloc[0], x.iloc[2] = x.iloc[2], x.iloc[0]

>>> x

A  1    3
   2    2
B  1    1
   2    4
dtype: int64

```

By the way, the `.from_tuples()` method, accepts a list of tuples like in the example, but aso a tuple of tuples like so:

```python

ser = pd.Series([1, 2, 3, 4], 
                index = pd.MultiIndex.from_tuples( 
                    ((a, b) for a, b in product(["A", "B"], [1, 2])), 
                    names = ["group", "number"] ))

```

But in fact this code is explicit but redundant and prone to performance loss, because `itertools.product` already `yields` tuples, so no ned to decompose to create tuples here, hence I can simply do:

```python

>>> ser = pd.Series([1, 2, 3, 4], 
                    index = pd.MultiIndex.from_tuples( 
                        product(["A", "B"], [1, 2]), 
                        names = ["group", "number"] 
                        )
                    )

```

Even better, just use the `.from_product()` method (no need to explicitly import and call `itertools.product`):

```python

ser = pd.Series([1, 2, 3, 4], 
                    index = pd.MultiIndex.from_product( 
                        [["A", "B"], [1, 2]], 
                        names = ["group", "number"] 
                        )
                )

```


Another `pd.MultiIndex` constructor is `.from_arrays()`:

```python

pd.MultiIndex.from_arrays(
    [["A", "A", "B", "B"], [1, 2, 1, 2]],
    names=["group", "number"],
)

```

Internally, python stores something like:

```

levels:
  level 0: Index(["A", "B"])
  level 1: Index([2023, 2024])

codes:
  code 0: [0, 0, 1, 1]
  code 1: [0, 1, 0, 1]

```

You can inspect levels of the index:

```python

>>> x.index.levels
FrozenList([['A', 'B'], [1, 2]])

```

And the `codes`:

```python

>>> ser.index.codes
FrozenList([[0, 0, 1, 1], [0, 1, 0, 1]])

```

Note, that is not boolean mask at all, just lists that for each level, stores the corresponding group as its index in the corresponding level.

`FrozenList` is a special `pandas` datatype that stipulates a list that should not be modified.

To get the names of the levels do:

```python

>>> x.index.names
FrozenList(['group', 'number'])

```

Rename them:

```python

x.index = x.index.set_names(["Group", "Number"])

```

On `Series/DataFrame`, `.rename_axis()` is an alias to `.set_names()` for the related `Index`:

```python

x = x.rename_axis(["Group", "Number"])

```

Now you have the filtering by `Index` values for free !

```python

>>> x[(x.index.codes[0] == 1) & (x.index.codes[1] == 0)]

Group  Number
B      1         2
dtype: int64

```

Or, you can just simply do:

```python

>>> x.loc[("B", 1)]
np.int64(2)

```

Here, it just returns a `numpy int64` because just one match.

But of course, if I have multiple matches, the returned type is a `pd.Series` whose `Index` is a `MultiIndex`:

```python

>>> ser1
A  1    1
   1    2
B  1    3
   2    4
dtype: int64

>>> ser1[("A", 1)]
A  1    1
   1    2
dtype: int64

```

But in fact this is not even the rule, because look at the returned type for a key that has one match from this example:

```python

>>> ser1.loc[("B", 1)]
B  1    3
dtype: int64

```

That's right, also a `pd.Series` (with `MultiIndex` index).

The rule is: If I have only uniques keys in the `index` attribute, then it will return a scalar, else a `pd.Series` with the corresponding `Index` type even if the current key we are searching is unique (because the whole `index` does not garuantee uniqueness, hence the scalar retuned type).

But if you want predictable return type do:

```python

>>> x.loc[[("B", 1)]]
Group  Number
B      1         2
dtype: int64

```

This will always be a `pd.Series`.

Of course, you can filter by bigger groups:

```python

>>> x.loc[("B", )]

Number
1    2
2    3
dtype: int64

>>> type(x.loc[("B", )])

<class 'pandas.Series'>

```

Now let's take a look at the follwoing example:

```python

>>> x = pd.MultiIndex.from_tuples([ (a, b, c) for a, b, c in product(["A", "B"], [1, 2], ["T", "E"]) ], names = ["g1", "g2", "g3"])>>> x
MultiIndex([('A', 1, 'T'),
            ('A', 1, 'E'),
            ('A', 2, 'T'),
            ('A', 2, 'E'),
            ('B', 1, 'T'),
            ('B', 1, 'E'),
            ('B', 2, 'T'),
            ('B', 2, 'E')],
           names=['g1', 'g2', 'g3'])

>>> ser = pd.Series(np.arange(8), index = x)

>>> ser
g1  g2  g3
A   1   T     0
        E     1
    2   T     2
        E     3
B   1   T     4
        E     5
    2   T     6
        E     7
dtype: int64

```

Now, let's perform `.loc` on the first level and the 2 firsts level:

```python

>>> ser.loc[("A", )]
g2  g3
1   T     0
    E     1
2   T     2
    E     3
dtype: int64

>>> ser.loc[("A", 1, )]
g3
T    0
E    1
dtype: int64

```

But, when I  don't want to precise the first or second level:

```python

>>> ser.loc[("A", , "T")]
  File "<stdin>", line 1
    ser.loc[("A", , "T")]
                  ^
SyntaxError: invalid syntax

>>> ser.loc[(, 2, "T")]
  File "<stdin>", line 1
    ser.loc[(, 2, "T")]
             ^
SyntaxError: invalid syntax

```

The problem only comes from the tuple synthax.

In fact, we must explicitly state that for the non-precised non-ending levels, we must precise that we want to select all of them.

And how to do it ?

Maybe with `:` ?

And yess, but with its formal notation `slice(None)`, because `:` is not interpreted in slices, but it semantically describe the same intent:

```python

>>> list(range(5))[:]
[0, 1, 2, 3, 4]

>>> list(range(5))[slice(None)]
[0, 1, 2, 3, 4]

```

Then, we'll use it like:

```python

>>> ser.loc[(slice(None), 2, "T")]
g1
A    2
B    6
dtype: int64

>>> ser.loc[(slice(None), slice(None), "T")]
g1  g2
A   1     0
    2     2
B   1     4
    2     6
dtype: int64

```

It's the same thing with `.index.get_loc()`.

The following works:

```python

>>> ser.index.get_loc(('A', 1, ))
slice(np.int64(0), np.int64(2), None)

>>> ser.index.get_loc(('A', ))
slice(np.int64(0), np.int64(4), None)

```

But not:

```python

>>> ser.index.get_loc((, 2, 'T'))
  File "<stdin>", line 1
    ser.index.get_loc((, 2, 'T'))
                       ^
SyntaxError: invalid syntax

>>> ser.index.get_loc(('A', , 'T'))
  File "<stdin>", line 1
    ser.index.get_loc(('A', , 'T'))
                            ^
SyntaxError: invalid syntax

```

Or even:

```python

>>> ser.index.get_loc(('A', , ))
  File "<stdin>", line 1
    ser.index.get_loc(('A', , ))
                            ^
SyntaxError: invalid syntax

```

While the semantic intent is the same as for:

```python

>>> ser.index.get_loc(('A', ))
slice(np.int64(0), np.int64(4), None)

```

Because, the synthax rule is no empty value beween 2 values of a tuple, so again use `slice(None)`:

```python

>>> ser.index.get_loc( ('A', slice(None), 'T') )
Traceback (most recent call last):
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/base.py", line 3641, in get_loc
    return self._engine.get_loc(casted_key)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "pandas/_libs/index.pyx", line 168, in pandas._libs.index.IndexEngine.get_loc
  File "pandas/_libs/index.pyx", line 176, in pandas._libs.index.IndexEngine.get_loc
  File "pandas/_libs/index_class_helper.pxi", line 70, in pandas._libs.index.Int64Engine._check_type
KeyError: slice(None, None, None)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/multi.py", line 3536, in get_loc
    return self._engine.get_loc(key)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "pandas/_libs/index.pyx", line 848, in pandas._libs.index.BaseMultiIndexCodesEngine.get_loc
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/base.py", line 3647, in get_loc
    raise InvalidIndexError(key) from err
pandas.errors.InvalidIndexError: slice(None, None, None)

```

Ho wait why ?

It's because `.get_loc` only accepts label key.

Therefore, here `slice(None)` is literally treated as a level, so even if it does respect the tuple synthax, it won't work.

For that, we use `.get_locs`

```python

>>> ser.index.get_locs( ('A', slice(None), 'T') )
array([0, 2])

```

Btw, here is an example where it is monotonicly sorted and contiguous so `.get_locs` returns a slice and `.get_locs()` returns an array of positions, like `.get_indexer_for` concerning the return type:

```python

>>> x3 = pd.MultiIndex(
...     levels=[
...         list("abc"),
...         [1, 2, 3],
...     ],
...     codes=[
...         np.repeat(
...             [0, 0, 0, 1, 1, 1, 2, 2, 2],
...             10,
...         ),
...         np.repeat(
...             [0, 1, 2] * 3,
...             10,
...         ),
...     ],
... )


>>> x3.get_loc(('a', 1))
slice(np.int64(0), np.int64(10), None)

>>> x3.get_locs(('a', 1))
array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

```

Now, let's try to infere the implementation of `.loc`.

Taking this query for example:

```python

ser.loc[("A", 1, "E")]

```

Which returns `npint64(1)` on the example:

```python

>>> ser.loc[("A", 1, "E")]
np.int64(1)

```

At first glance, because `.index.levels` are standard `pd.Index` related to `.index.codes` array, we can think that it roughly does the following:

```python

>>> np.intersect1d(
        np.intersect1d(
            locate_code(ser.index.codes[0] == ser.index.levels[0].get_loc("A")), 
            locate_code(ser.index.codes[1] == ser.index.levels[1].get_loc(1))
        ), 
        locate_code(
            ser.index.codes[2] == ser.index.levels[2].get_loc("E")
        ) 
    )

```

We can expand the expression replacing `locate_code` with a known function such as `np.where()` even if it must use hashmap or binary search own implemntation:

```python

>>> np.intersect1d(
        np.intersect1d(
            np.where(ser.index.codes[0] == ser.index.levels[0].get_loc("A")), 
            np.where(ser.index.codes[1] == ser.index.levels[1].get_loc(1))
        ), 
        np.where(
            ser.index.codes[2] == ser.index.levels[2].get_loc("E")
        ) 
    )

```

And it returns the good result but not as the correct type:

```python

array([1])

```

But this approach is ineficient because it must perform `len(levels)` scans and apply the intersection.

It would be faster to maintain only one internal `index` array that for each position has an hash of the code levels.

Like:

```

2, 0, 1 -> hash1
2, 0, 0 -> hash2
2, 0, 1 -> hash1
1, 0, 1 -> hash3
...

```

So, this is a small cost to maintain this structure when the levels changes position, are added / deleted etcetera, but bring a more efficient row selection model.

And from what I have searched this is the conceptual model:

```python

key_codes = (
    mi.levels[0].get_loc("A"),
    mi.levels[1].get_loc(1),
    mi.levels[2].get_loc("E"),
)

combined_key = encode(key_codes)

position = mi._engine.get_loc(combined_key)

```

But this does not explain the `.get_locs()` with `slice(None)` behavior, at one or more levels, none is specified.

From what I think is the optimal solution, is just to perform `.get_loc` for as many unspecified keys there are and combine the results.

Then we have the array of positions (slice or boolean vector) and we can use `.iloc`.

Let's benchmark it, first with sorted keys:

```python

import pandas as pd
import matplotlib.pyplot as plt
import time, math
import numpy as np
from itertools import product

xs = list(range(1_000, 2_000_000, 100_000))
ys = []

n_repeats = 10_000

rng = np.random.default_rng(55)

lvls = [ ['A', 'B', 'C'], [1, 2], ['T', 'E'] ]

rep_val = math.prod([ len(x) for x in lvls ])

original_sz = rep_val

codes = []

for pr in lvls:

    sz = len(pr)

    cur_arr = np.arange(0, sz)
    
    cur_arr = np.repeat(cur_arr, np.full(sz, rep_val // sz))

    itr = original_sz // rep_val

    if itr > 0: cur_arr = np.tile(cur_arr, itr)

    codes.append(cur_arr)

    rep_val //= sz

lvls_choice = [x for x in product(*lvls)]

base_val = math.prod([len(x) for x in lvls])
# OR
#base_val = np.array([len(x) for x in levels]).prod()

for n in xs:

    hmn = n // base_val
    counts = np.full(base_val, hmn, dtype = np.int32)
    counts[: n % base_val] += 1

    cur_codes = []
    for i in range(len(lvls)):
        cur_codes.append(np.repeat(codes[i], counts))

    idx = pd.MultiIndex(
            levels = lvls,
            codes = cur_codes,
            names = ["g1", "g2", "g3"]
          )
    keys_indices = rng.integers(0, len(lvls_choice), size = n_repeats)
    keys = [lvls_choice[i] for i in keys_indices]

    #keys = rng.choice(lvls_choice, size = n_repeats)

    print("ok", keys[0])

    idx.get_loc(keys[0])

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure_multi_index.png")

```

The important part here is that I construct the `pd.MultiIndex` by providing the codes for the same reson I did the equivalent for the `pd.CategoricalIndex`, because it's faster -> no need to build the internal codes by scanning the keys values.

But to construct the codes monotonicly increasing, what kind of algo to use ?

Hmm, cartesian product !

Look for examplehere I can generate all the combinations between 8 `[0, 1]` lists to generate all the possible states of a byte:

```python

>>> lst = [x for x in product([0, 1], repeat = 8)]

>>> len(lst)
256

>>> lst[slice(0, len(lst), 30)]
[(0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 1, 1, 1, 1, 0), (0, 0, 1, 1, 1, 1, 0, 0), (0, 1, 0, 1, 1, 0, 1, 0), (0, 1, 1, 1, 1, 0, 0, 0), (1, 0, 0, 1, 0, 1, 1, 0), (1, 0, 1, 1, 0, 1, 0, 0), (1, 1, 0, 1, 0, 0, 1, 0), (1, 1, 1, 1, 0, 0, 0, 0)]

```

But as you see it returns a list of tuples, not what I want because the API is very clear, for 3 levels we have forexample:

```python

pd.MultiIndex(
    levels = [ cat1, cat2, cat3 ]
    codes = [ codes1, codes2, codes3 ],
    names = ["group1", "group2", "group3"]
)

```

where `catN` and `codesN` are lists.

Another example for a 2 levels `pd.MultiIndex`:

```python

>>> x = pd.MultiIndex(levels = [ ["A", "B"], [1, 2]], codes = [ [0, 0, 1, 1] , [0, 1, 0, 1] ], names = ["g1", "g2"])
>>> x
MultiIndex([('A', 1),
            ('A', 2),
            ('B', 1),
            ('B', 2)],
           names=['g1', 'g2'])

```

Therefore, we need to provide the codes a list of list, each list representing the codes for the associated level.

When you saw the that:

```python

[ [0, 0, 1, 1] , [0, 1, 0, 1] ]

```

You can recognize a pattern.

The repetition of each unique code value is conditioned to its level position and the sum of unique values it has for this level.

Like in this example:

```python

[ 
  ["A", "B", "C"],
  [1, 2],
  ["T", "E"]

]

```

We can consider the following:

1. What is the current pattern for this level ?

- At the first level, the pattern is built with `len(level1) * len(level2) * len(level3) => 3 * 2 * 2 = 12` values.

- At the second level, the pattern is built with `len(level1) * len(level2) => 2 * 2 = 4` values.

- At the third level, the pattern is built with `len(level1) => 2 = 2` values.

2. How much should we repeat each unqiue key at this level ?

- At the first level, it's `total_unique_combinations_at_this_level / unique_values_at_this_level => 12 / 3 = 4`

- At the first level, it's `total_unique_combinations_at_this_level / unique_values_at_this_level => 4 / 2 = 4`

- At the first level, it's `total_unique_combinations_at_this_level / unique_values_at_this_level => 2 / 2 = 4`

3.

- Should we repeat this patter to match the size of all the possible combinations ?

- At the first level, no because ` total_unique_combinations / ( len(level1) * len(level2) * len(level3) )= 1`.

- At the second -> yes -> `total_unique_combinations / ( len(level1) * len(level2) )= 3` times

- At the third -> yes -> `total_unique_combinations / len(level1)= 6` times

That is exactly this implementation:

```python

for pr in lvls:

    sz = len(pr)

    cur_arr = np.arange(0, sz)
    
    cur_arr = np.repeat(cur_arr, np.full(sz, rep_val // sz))

    itr = original_sz // rep_val

    if itr > 1: cur_arr = np.tile(cur_arr, itr)

    codes.append(cur_arr)

    rep_val //= sz

```

To avoid the remaining allocation due to `tile`, we can allocate once since we know in advance the size of the array and then set the values manually:

```python

for pr in lvls:

    sz = len(pr)

    cur_arr = np.empty(original_sz, 0)

    cur_sz = rep_val // sz

    for i in range(sz): 
        cur_arr[i * cur_sz : (i + 1) * cur_sz] = i

    itr = original_sz // rep_val

    if itr > 1:
        for i in range(1, itr):
            cur_arr[i * rep_val : (i + 1) * rep_val] = cur_arr[0:rep_val]

    codes.append(cur_arr)

    rep_val //= sz

```

But lesswork happens inside `numpy` therefore it is not automatically faster.

Btw, we can simplify the initial version to:

```python

for level in lvls:
    sz = len(level)

    block_size = rep_val // sz
    itr = original_sz // rep_val

    cur_arr = np.tile(
        np.repeat(np.arange(sz), block_size),
        itr,
    )

    codes.append(cur_arr)
    rep_val //= sz

```

After this digression, here are the results:

![measure_multi_index.png](../assets/common_files/Matplotlib/measure_multi_index.png)

This is pretty fast and constant.

We do not clearly see the `O(log(n))` curve from `n = 1_000_000` to the end neither the big jump from pre `n = 1_000_000` to post `n = 1_000_000` because from what I've understood, it uses `np.searchsorted()` at every tested level.

Indeed, it's able to see in advance that the key values are monotonic, so it directly uses this method.

But of course, you could build your own hashmap and use it to select rows if you absolutely want to use this method:

```python

import pandas as pd
import matplotlib.pyplot as plt
import time, math
import numpy as np
from itertools import product
from collections import defaultdict

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 1_000

rng = np.random.default_rng(55)

lvls = [ ['A', 'B', 'C'], [1, 2], ['T', 'E'] ]

rep_val = math.prod([ len(x) for x in lvls ])

original_sz = rep_val

codes = []

for pr in lvls:

    sz = len(pr)

    cur_arr = np.arange(0, sz)
    
    cur_arr = np.repeat(cur_arr, np.full(sz, rep_val // sz))

    itr = original_sz // rep_val

    if itr > 1: cur_arr = np.tile(cur_arr, itr)

    codes.append(cur_arr)

    rep_val //= sz

lvls_choice = [x for x in product(*lvls)]

base_val = math.prod([len(x) for x in lvls])
# OR
#base_val = np.array([len(x) for x in levels]).prod()

for n in xs:

    hmn = n // base_val
    counts = np.full(base_val, hmn, dtype = np.int32)
    counts[: n % base_val] += 1

    cur_codes = []
    for i in range(len(lvls)):
        cur_codes.append(np.repeat(codes[i], counts))

    idx = pd.MultiIndex(
            levels = lvls,
            codes = cur_codes,
            names = ["g1", "g2", "g3"]
          )

    keys_indices = rng.integers(0, len(lvls_choice), size = n_repeats)
    keys = [lvls_choice[i] for i in keys_indices]

    hsh = defaultdict(list)
    for i, key in enumerate(idx.values):
        hsh[key].append(i)

    start = time.perf_counter()

    for key in keys:
        hsh[key]

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure_multi_index3.png")


```

Note that I could replace:

```python

for i, key in enumerate(idx.values):
    hsh[key].append(i)

```

by:

```python


for i, key in enumerate(zip(*idx.codes)):
    hsh[ tuple(idx.levels[i2][cur_idx] for i2, cur_idx in enumerate(key) ) ].append(i)

```

But since the key values of the `pd.MultiIndex` are already materialized, then I just use the first version.

And here are the results:

![measure_multi_index3.png](../assets/common_files/Matplotlib/measure_multi_index3.png)

Very fast.

Now, I will just reference the result to a variable like that:

```python

result = hsh[key]

```

Now, I have those results:

![measure_multi_index3b.png](../assets/common_files/Matplotlib/measure_multi_index3b.png)

Hoooo, wait why ?

At first, I create a `defaultdict(list)` and repeatedly execute `result = hsh[key]`. During the lookup loop, the lists are owned by `hsh`, while the most recently accessed list is additionally referenced by `result`.

At the beginning of the next outer iteration, `hsh` is replaced by a new dictionary. The old dictionary is then destroyed, which releases its references to all its lists. Every list is freed immediately except the last one, because `result` still references it.

The timer then starts while result still points to that old list. On the first assignment in the new lookup loop, `result` is redirected to a list from the new dictionary. The old list consequently loses its final reference and is destroyed at that moment.

Because this old list contains roughly `n / 12` positions, releasing all its elements costs roughly `O(n / 12)`. Since that deallocation occurs inside the timed region, it produces the apparently linear lookup time.

The fix is therefore simple, just put `result = None` at the beginning of the outer loop.

With `MultiIndex`, you also have `.xs()` method that does the same job but with explicit level selection:

```python

>>> x.xs(("B", ), drop_level=False)

Group  Number
B      1         2
       2         3
dtype: int64

>>> x.xs(("B", ), drop_level=True)

Number
1    2
2    3
dtype: int64

```

But maybe more intuitively because you can put the level index in the order you want and explicit the order afterward with the `level` argument:

```python

>>> ser.xs((1, "B"), level=("number", "group"), drop_level = False)

group  number
B      1         3
dtype: int64

>>> ser.xs(("B"), level=("group"), drop_level = True)

number
1    3
2    4
dtype: int64

>>> ser.xs((1), level=("number"), drop_level = True)

group
A    1
B    3
dtype: int64

```

Because you can not do the last example, with normal `.loc` synthax, because we can not declare a tuple as `(, 1)` for example, so this wont work:

```python

>>> ser[(, 1)]
  File "<stdin>", line 1
    ser[(, 1)]
         ^
SyntaxError: invalid syntax

```

There is also an interesting architectural choice that has been made here, until now, we have understood the concept of `drop_level` that literaly drop the level we are explicitely filtering on, this is logic and allow us to return a minimal `ps.Series`.

But what happens, when we filter on all levels, I mean the return type should still match the original data-structure, then having a `pd.MultiIndex`.

The choice `pandas` developper did was to literaly apply the behavior as if `drop_level = False`, even if you set it to `True`, it will act as if `False`, which is a bold but understable way to keep returned structure type intact.

But seriously, after all they did (not) for unpredictable data-type returned in other functions, who would have thought that they will insist on keeping data-type intact for this operation ?

Note; by default `drop_level` is set to `False`.

```python

>>> x.xs(("B", ))
Number
1    2
2    3
dtype: int64

```

Now, a use of the `.map()` method.

```python

idx = pd.MultiIndex.from_tuples(
    [("A", 1), ("A", 2), ("B", 1), ("B", 2)],
    names=["group", "num"],
)

idx.map(lambda x: f"{x[0]}-{x[1]}")

```

Output.

```

Index(['A-1', 'A-2', 'B-1', 'B-2'], dtype='str')

```

It collapsed the levels to 1, so it returned a `pd.Index`.

And yes, `pd.Index` values can absolutely be strings.

They can even be mixed, like for lists:

```python

>>> pd.Index([12, "D"])
Index([12, 'D'], dtype='object')

```

The same goes for `pd.MultiIndex`:

```python

>>> pd.MultiIndex.from_tuples(product(["F", 0], ["E", 1]))

MultiIndex([('F', 'E'),
            ('F',   1),
            (  0, 'E'),
            (  0,   1)],
           )

```

Of course it comes with all the common methods.

```python

idx1.union(idx2)
idx1.intersection(idx2)
idx1.difference(idx2)
idx1.symmetric_difference(idx2)

```

### `pd.DatetimeIndex()`

You can create one with `pd.date_range(start_date, period_repetition, time_unit)`.

One of the best predictable function for getting a proper time unit is `pd.DateOffset(time_unit)`

Then.

```python

>>> pd.date_range("2024-01-11 00:10:00", 
                  periods=15, 
                  freq=pd.DateOffset(weeks=1, hours=1),
                  tz="Europe/Paris")

DatetimeIndex(['2024-01-11 00:10:00+01:00', '2024-01-18 01:10:00+01:00',
               '2024-01-25 02:10:00+01:00', '2024-02-01 03:10:00+01:00',
               '2024-02-08 04:10:00+01:00', '2024-02-15 05:10:00+01:00',
               '2024-02-22 06:10:00+01:00', '2024-02-29 07:10:00+01:00',
               '2024-03-07 08:10:00+01:00', '2024-03-14 09:10:00+01:00',
               '2024-03-21 10:10:00+01:00', '2024-03-28 11:10:00+01:00',
               '2024-04-04 12:10:00+02:00', '2024-04-11 13:10:00+02:00',
               '2024-04-18 14:10:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq='<DateOffset: hours=1, weeks=1>')

```

Note that the type used is `pd.datetime64`, it tells the type of the `DatetimeIndex`, it stores datetime as datetime like integers with microseconds precision (`us`) and a timezone metadata are attcahed (`Europe/Paris`).

Also, note this constructor API looks a bit like the `RangeIndex` API, we got a start, we got a `freq` which is the `step` and the `end` is simply `start` + `freq` * `period`.

Annnnd, note that in the following text I may write datetime instead of timestamp and inversely, why ?

Because.

```python

>>> pd.to_datetime("2024-01-01")
Timestamp('2024-01-01 00:00:00')

```

Going back to the example...

But unfortunately, it just creates a big range of `pd.Timestamp` and it does not just store tiny object with `start`, `end` and `step`.

That could be usefull, maybe at some point, `pandas` team will introduce a `pd.RangeDatetimeIndex`, who knows... :=)

Now you can do:

```python

>>> ser = pd.Series([1,2,3], index=pd.date_range("2024-01-01", periods=3, freq="D"))

>>> ser["2024-01-02"]

np.int64(2)

```

Or even slicing:

```python

>>> ser["2024-01-01":"2024-01-05"]

2024-01-01    1
2024-01-02    2
2024-01-03    3
Freq: D, dtype: int64

```

To describe time difference, we have `pd.Timedelta()` and `pd.DateOffset()`.

In fact `pd.DateOffset` is very specific:

```python

ts + pd.DateOffset(days = 1)

```

Means: "Go to the same local clock time the next day" (it guarantees it, not like `ts + pd.Timedelta(hours = 24)`).

For time unit between hour and less, `pd.DateOffset()` and `pd.Timedelta()` are the same, because that are fixed time unit.

But as we begin to speak about day, by how many hours it is made of, 24 hours ? Yesss, but sometimes in the year it is 23 hours or 25 hours.

So at this moment it starts to differe.

Btw, `Timedelta` does not have `weeks`, `months` or `years`,it is a pure contant duration and not aware of the calendar contrary to `pd.DateOffset()`.

Then use `pd.Timedelta(time_unit)` when yo want to ADD a fixed duration.

And use `pd.DateOffset(time_unit)` when you want "the same date of **origin** + an offset of the unit time but **aware of calendar - interpreted by the calendar accoding to the local TimeZone**"

`pd.DateOffset` is therefore inherently dependant of the origin (the context) where it is applied for the current computation.

So after saying this you know that those are equivalent.

```python

>>> pd.Timestamp("2024-01-01 11:10:00") + pd.Timedelta(minutes=1, hours=2)

Timestamp('2024-01-01 13:11:00')

>>> pd.Timestamp("2024-01-01 11:10:00") + pd.DateOffset(minutes=1, hours=2)

Timestamp('2024-01-01 13:11:00')

```

Or with the string syntyhax equivalnt for `pd.TimeDelta`:

```python

>>> pd.Timestamp("2024-01-01 11:10:00") + pd.Timedelta("2h 1min") # or 2 hours 1 minute

Timestamp('2024-01-01 13:11:00')

>>> pd.Timestamp("2024-01-01 11:10:00") + pd.DateOffset(minutes=1, hours=2)

Timestamp('2024-01-01 13:11:00')

```

Even those:

```python

>>> pd.date_range("2024-01-11 00:10:00", periods=15, freq=pd.DateOffset(minutes=1, hours=2), tz="Europe/Paris")

DatetimeIndex(['2024-01-11 00:10:00+01:00', '2024-01-11 02:11:00+01:00',
               '2024-01-11 04:12:00+01:00', '2024-01-11 06:13:00+01:00',
               '2024-01-11 08:14:00+01:00', '2024-01-11 10:15:00+01:00',
               '2024-01-11 12:16:00+01:00', '2024-01-11 14:17:00+01:00',
               '2024-01-11 16:18:00+01:00', '2024-01-11 18:19:00+01:00',
               '2024-01-11 20:20:00+01:00', '2024-01-11 22:21:00+01:00',
               '2024-01-12 00:22:00+01:00', '2024-01-12 02:23:00+01:00',
               '2024-01-12 04:24:00+01:00'],
              dtype='datetime64[us, Europe/Paris]', freq='<DateOffset: hours=2, minutes=1>')

>>> pd.date_range("2024-01-11 00:10:00", periods=15, freq=pd.Timedelta(minutes=1, hours=2), tz="Europe/Paris")

DatetimeIndex(['2024-01-11 00:10:00+01:00', '2024-01-11 02:11:00+01:00',
               '2024-01-11 04:12:00+01:00', '2024-01-11 06:13:00+01:00',
               '2024-01-11 08:14:00+01:00', '2024-01-11 10:15:00+01:00',
               '2024-01-11 12:16:00+01:00', '2024-01-11 14:17:00+01:00',
               '2024-01-11 16:18:00+01:00', '2024-01-11 18:19:00+01:00',
               '2024-01-11 20:20:00+01:00', '2024-01-11 22:21:00+01:00',
               '2024-01-12 00:22:00+01:00', '2024-01-12 02:23:00+01:00',
               '2024-01-12 04:24:00+01:00'],
              dtype='datetime64[us, Europe/Paris]', freq='121min')

```

But, not passed `hours` time unit where semantic differes A LOT.

The units of `pd.TimeDelta` are:

```python

pd.Timedelta(3, unit="D")   # days
pd.Timedelta(3, unit="h")   # hours
pd.Timedelta(3, unit="m")   # minutes
pd.Timedelta(3, unit="s")   # seconds
pd.Timedelta(3, unit="ms")  # milliseconds
pd.Timedelta(3, unit="us")  # microseconds
pd.Timedelta(3, unit="ns")  # nanoseconds

```

And for `DateOffset`:

```python

pd.DateOffset(
    years=1,
    months=2,
    weeks=3,
    days=4,
    hours=5,
    minutes=6,
    seconds=7,
    milliseconds=8,
    microseconds=9,
    nanoseconds=10,
)

```

For creating `DateIndex`, you also have shortcuts and new concepts, like next month/year start/end, buisness days...

```

s       seconds
min     minutes
h       hours
D       days
B       business days
W       weeks
MS      month start
ME      month end
QS      quarter start
QE      quarter end
YS      year start
YE      year end

```

Basic units, like seconds.

```python

>>> pd.date_range("2024-01-11 00:10:00", periods=15, freq="s")

DatetimeIndex(['2024-01-11 00:10:00', '2024-01-11 00:10:01',
               '2024-01-11 00:10:02', '2024-01-11 00:10:03',
               '2024-01-11 00:10:04', '2024-01-11 00:10:05',
               '2024-01-11 00:10:06', '2024-01-11 00:10:07',
               '2024-01-11 00:10:08', '2024-01-11 00:10:09',
               '2024-01-11 00:10:10', '2024-01-11 00:10:11',
               '2024-01-11 00:10:12', '2024-01-11 00:10:13',
               '2024-01-11 00:10:14'],
              dtype='datetime64[us]', freq='s')

```

You can also associate an ingeter to jump `n` unit of time (`"5s"`).

```python

>>> pd.date_range("2024-01-11 00:10:00", periods=15, freq="5s")

DatetimeIndex(['2024-01-11 00:10:00', '2024-01-11 00:10:05',
               '2024-01-11 00:10:10', '2024-01-11 00:10:15',
               '2024-01-11 00:10:20', '2024-01-11 00:10:25',
               '2024-01-11 00:10:30', '2024-01-11 00:10:35',
               '2024-01-11 00:10:40', '2024-01-11 00:10:45',
               '2024-01-11 00:10:50', '2024-01-11 00:10:55',
               '2024-01-11 00:11:00', '2024-01-11 00:11:05',
               '2024-01-11 00:11:10'],
              dtype='datetime64[us]', freq='5s')

```

Now, concept of Buisnes, Month Start `"MS"` and Month End `"ME"`.

`"MS"` is the next date of a beginning of a month.

```python

>>> pd.date_range("2024-01-11 00:10:00", periods=15, freq="MS", tz="Europe/Paris")

DatetimeIndex(['2024-02-01 00:10:00+01:00', '2024-03-01 00:10:00+01:00',
               '2024-04-01 00:10:00+02:00', '2024-05-01 00:10:00+02:00',
               '2024-06-01 00:10:00+02:00', '2024-07-01 00:10:00+02:00',
               '2024-08-01 00:10:00+02:00', '2024-09-01 00:10:00+02:00',
               '2024-10-01 00:10:00+02:00', '2024-11-01 00:10:00+01:00',
               '2024-12-01 00:10:00+01:00', '2025-01-01 00:10:00+01:00',
               '2025-02-01 00:10:00+01:00', '2025-03-01 00:10:00+01:00',
               '2025-04-01 00:10:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq='MS')

```

Same for `"ME"`.

```python

>>> pd.date_range("2024-01-11 00:10:00", periods=15, freq="ME", tz="Europe/Paris")

DatetimeIndex(['2024-01-31 00:10:00+01:00', '2024-02-29 00:10:00+01:00',
               '2024-03-31 00:10:00+01:00', '2024-04-30 00:10:00+02:00',
               '2024-05-31 00:10:00+02:00', '2024-06-30 00:10:00+02:00',
               '2024-07-31 00:10:00+02:00', '2024-08-31 00:10:00+02:00',
               '2024-09-30 00:10:00+02:00', '2024-10-31 00:10:00+01:00',
               '2024-11-30 00:10:00+01:00', '2024-12-31 00:10:00+01:00',
               '2025-01-31 00:10:00+01:00', '2025-02-28 00:10:00+01:00',
               '2025-03-31 00:10:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq='ME')

```

Those are possible because internaly it must use timezone calendar aware (`pd.DateOffset(...)` ...).

Same concept for `"YS"` and `"YE"`.

Here is a more about time unit:

```python

# sub-day
freq="s"       # seconds
freq="min"     # minutes
freq="h"       # hours

# day/week
freq="D"       # calendar days
freq="B"       # business days, Monday-Friday
freq="W"       # weekly, default ends on Sunday
freq="W-MON"   # weekly, anchored on Monday

# month
freq="MS"      # month start
freq="ME"      # month end

# quarter
freq="QS"      # quarter start
freq="QE"      # quarter end

# year
freq="YS"      # year start
freq="YE"      # year end

```

Note that `"W"` is basically a shortcut for `"W-SUN"`.

You can have by Tuesday for example, with `"W-TUE"`.

```pyhton

>>> pd.date_range("2024-01-11 00:10:00", periods=15, freq="W-TUE", tz="Europe/Paris")

DatetimeIndex(['2024-01-16 00:10:00+01:00', '2024-01-23 00:10:00+01:00',
               '2024-01-30 00:10:00+01:00', '2024-02-06 00:10:00+01:00',
               '2024-02-13 00:10:00+01:00', '2024-02-20 00:10:00+01:00',
               '2024-02-27 00:10:00+01:00', '2024-03-05 00:10:00+01:00',
               '2024-03-12 00:10:00+01:00', '2024-03-19 00:10:00+01:00',
               '2024-03-26 00:10:00+01:00', '2024-04-02 00:10:00+02:00',
               '2024-04-09 00:10:00+02:00', '2024-04-16 00:10:00+02:00',
               '2024-04-23 00:10:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq='W-TUE')

```

Here, it takes the origin date, moves to next Tuesday and by this one add one week for a period of `15` times.

Then all dates here are Tuesdays.

Here are all the variants:

```

"W-MON"  # weekly, anchored on Monday
"W-TUE"  # weekly, anchored on Tuesday
"W-WED"  # weekly, anchored on Wednesday
"W-THU"  # weekly, anchored on Thursday
"W-FRI"  # weekly, anchored on Friday
"W-SAT"  # weekly, anchored on Saturday
"W-SUN"  # weekly, anchored on Sunday

```

Of course it has all basic `Index` methods plus a bunch of specific date methods.

First, of course you can extract a time unit for each one of its element.

```python

>>> x

DatetimeIndex(['2024-01-16 00:10:00+01:00', '2024-01-23 00:10:00+01:00',
               '2024-01-30 00:10:00+01:00', '2024-02-06 00:10:00+01:00',
               '2024-02-13 00:10:00+01:00', '2024-02-20 00:10:00+01:00',
               '2024-02-27 00:10:00+01:00', '2024-03-05 00:10:00+01:00',
               '2024-03-12 00:10:00+01:00', '2024-03-19 00:10:00+01:00',
               '2024-03-26 00:10:00+01:00', '2024-04-02 00:10:00+02:00',
               '2024-04-09 00:10:00+02:00', '2024-04-16 00:10:00+02:00',
               '2024-04-23 00:10:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq='W-TUE')

>>> x.year

Index([2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024,
       2024, 2024, 2024],
      dtype='int32')

```

Here, they are.

```python

idx.year
idx.month
idx.day
idx.hour
idx.minute
idx.second
idx.microsecond
idx.nanosecond

```

Or more specific:

```python

idx.dayofweek      # Monday=0, Sunday=6
idx.day_of_week    # same idea
idx.dayofyear
idx.day_of_year # same as above lol
idx.quarter
idx.days_in_month # hw many days in current month

```

Start / End flags

```python

idx.is_month_start
idx.is_month_end
idx.is_quarter_start
idx.is_quarter_end
idx.is_year_start
idx.is_year_end
idx.is_leap_year

```

There is no, `is_week_start` or `is_week_end`, so use `day_of_week` index logic (0 - 6) (Monday - Sunday).

To get the step of time unit a `DatetimeIndex`:

```python

>>> x.freq
<Week: weekday=1>

```

Note, `weekday = 1` indicates that is the second day of the week, hence a Tuesday like we defined.

Or in string:

```python

>>> x.freqstr
'W-TUE'

```

But, this only is set to this value because we constructed the `DatetimeIndex` with `date_range()` constructor superset that puts a value to the frequency.

Because with standard frequency:

```python

>>> pd.DatetimeIndex([pd.Timestamp("2024-01-01 00:00:00"), pd.Timestamp("2024-01-02 07:12:03")]).freq

```

We got no result.

But if your date are separated by a constant step, you can ask pandas to infere.

```python

>>> pd.DatetimeIndex([
                pd.Timestamp("2024-01-01 00:00:00"), 
                pd.Timestamp("2024-01-02 07:12:03"), 
                pd.Timestamp("2024-01-03 14:24:06")]).inferred_freq
'112323s'

```

You can also get the numpy array of python standard datetime.

```python

>>> from datetime import datetime

>>> x.date
array([datetime.date(2024, 1, 16), datetime.date(2024, 1, 23),
       datetime.date(2024, 1, 30), datetime.date(2024, 2, 6),
       datetime.date(2024, 2, 13), datetime.date(2024, 2, 20),
       datetime.date(2024, 2, 27), datetime.date(2024, 3, 5),
       datetime.date(2024, 3, 12), datetime.date(2024, 3, 19),
       datetime.date(2024, 3, 26), datetime.date(2024, 4, 2),
       datetime.date(2024, 4, 9), datetime.date(2024, 4, 16),
       datetime.date(2024, 4, 23)], dtype=object)

```

Btw, here an explanaton on differences between `datetime.datetime.date` and `pd.Timestamp`.

They represent similar things, but `Timestamp` is built to fit `pandas/NumPy` time-series machinery.

Basic similitudes in construction:

```python

from datetime import datetime
import pandas as pd

dt = datetime(2024, 1, 16, 12, 30) # year, month, day, hour, minutes, seconds...

ts1 = pd.Timestamp("2024-01-16 12:30")
ts2 = pd.Timestamp(2024, 1, 16, 12, 30)
ts3 = pd.Timestamp(dt)

```

There is also a differnce between `datetime.datetime` and `datetime.date`, `datetime.date` stores only the calendar date `year + month + day`, while `datetime.datetime` stores the date plus the time of the day.

```python

>>> from datetime import datetime, date

>>> date(2024, 1, 16)

datetime.date(2024, 1, 16)

>>> datetime(2024, 1, 16, 12, 30, 13)

datetime.datetime(2024, 1, 16, 12, 30, 13)

>>> datetime(2024, 1, 16, 12, 30, 13).date()

datetime.date(2024, 1, 16)

```

`datetime.date` is a lighter object than `datetime.datetime`:

```python

>>> import sys

>>> sys.getsizeof(datetime(2024, 1, 16, 12, 30, 13).date())

32

>>> sys.getsizeof(datetime(2024, 1, 16, 12, 30, 13))

48

```

And a `pd.Timestamp` is the heaviest:

```python

>>> sys.getsizeof(pd.Timestamp(2024, 2, 12))

120

```

Of course, their type differe:

```python

>>> type(dt)

datetime.datetime

```

```python

>>> type(ts)

pandas._libs.tslibs.timestamps.Timestamp

```

`pd.Timestamp` is mostly compatible with `datetime.datetime`, but has extra pandas behavior.

Precision

Python `datetime.datetime` supports microseconds:

```

2024-01-16 12:30:00.123456

```

Pandas Timestamp supports finer precision, usually nanoseconds:

```python

>>> pd.Timestamp("2024-01-16 12:30:00.123456789")

Timestamp('2024-01-16 12:30:00.123456789')

```

Python datetime can not represent the last `789` nanoseconds directly.

Missing values

Pandas has a datetime missing value:

```python

pd.NaT

```

-> Not a Time

Example:

```python

>>> pd.to_datetime(["2024-01-01", None])
DatetimeIndex(['2024-01-01', 'NaT'], dtype='datetime64[ns]', freq=None)

```

Python `datetime` has no native datetime-specific `NaT`; you usually use None.

Vectorization

Python `datetime` is a scalar object. If you have many of them in a list, operations are Python-loop-ish:

```python

dates = [datetime(2024, 1, 1), datetime(2024, 1, 2)]

```

Pandas uses `Timestamp` scalars plus `DatetimeIndex / Series[datetime64]` arrays:

```python

idx = pd.date_range("2024-01-01", periods=3, freq="D")

idx.year
idx.month
idx + pd.Timedelta(days=1)

```

Here, `.date_range()` is a vectorized operation.

`Timezone` handling

Both can be timezone-aware:

```python

>>> ts = pd.Timestamp("2024-03-31 12:00", tz="Europe/Paris")

>>> ts.tz_convert("UTC")

Timestamp('2024-03-31 10:00:00+0000', tz='UTC')

```

With Python `datetime`:

```python

from datetime import timezone, datetime

dt = datetime(2024, 3, 31, 12, 0, tzinfo=timezone.utc)

```

But the `pd.Timestamp` timezone changes is a vectorized operation for all `pd.Timestamp` in a `pd.DatetimeIndex`:

```python

idx_utc = pd.date_range(
    "2024-01-01 12:00",
    periods=3,
    freq="D",
    tz="UTC"
)

idx_paris = idx_utc.tz_convert("Europe/Paris")

```

Result:

```python

DatetimeIndex(['2024-01-01 13:00:00+01:00', '2024-01-02 13:00:00+01:00',
               '2024-01-03 13:00:00+01:00'],
              dtype='datetime64[us, Europe/Paris]', freq=None)

```

Or when attaching a `timezone` to date that does not have one:

```python

>>> idx = pd.date_range("2024-01-01 12:00", periods=3, freq="D")

>>> idx
>>> DatetimeIndex(['2024-01-01 12:00:00',
                   '2024-01-02 12:00:00',
                   '2024-01-03 12:00:00'],
                  dtype='datetime64[ns]', freq='D')

>>> idx_paris = idx.tz_localize("Europe/Paris")

>>> DatetimeIndex(['2024-01-01 12:00:00+01:00',
                   '2024-01-02 12:00:00+01:00',
                   '2024-01-03 12:00:00+01:00'],
                  dtype='datetime64[ns, Europe/Paris]', freq=None)

```

Note that those operations make the `pd.DatetimeIndex` lose its frequency, which is a metadata that we can reattach it like this:

```python

>>> idx = pd.DatetimeIndex(idx, freq = idx.tz_convert("Europe/Paris").inferred_freq)
>>> idx
DatetimeIndex(['2024-01-01 12:00:00+00:00', '2024-01-02 12:00:00+00:00',
               '2024-01-03 12:00:00+00:00'],
              dtype='datetime64[us, UTC]', freq='D')

```

Note that when you create a `datetime.datetime`, you have to precise year, month and day, others are set to default `0` value.

Date arithmetic

Python:

```python

from datetime import timedelta

dt + timedelta(days=1)

```

Pandas:

```python

ts + pd.Timedelta(days=1)
ts + pd.DateOffset(months=1) # for calendar aware offset

```

The important pandas-specific part is `DateOffset`:

```python

>>> pd.Timestamp("2024-01-31") + pd.DateOffset(months=1)

Timestamp('2024-02-29 00:00:00')

```

As intended, Python’s `timedelta` has no “months” because months are not fixed durations.

Range / limits

`pandas` `Timestamps` backed by NumPy-style nanosecond datetimes have a limited range, roughly years 1677 to 2262 for nanosecond precision.

Python datetime supports years 1 to 9999.

So this works in Python:

```python

datetime(3000, 1, 1)

```

But may not fit into pandas’ nanosecond `datetime` `dtype` cleanly.

Conversion

Python datetime to `pandas` timestamp:

```python

ts = pd.Timestamp(datetime(2024, 1, 16, 12, 30))

```

`pd.Timestamp` to Python `datetime`:

```python

dt = ts.to_pydatetime()

```

Date-only Python object:

```python

>>> ts.date()
datetime.date(2024, 1, 16)

```

-> Loss of precision here (as we have already seen, stores just day-month-year, not clock time)

Or if you want the time (not the date part) from a `DatetimeIndex`, you can do that for example:

```python

>>> x.time

array([datetime.time(0, 10), datetime.time(0, 10), datetime.time(0, 10),
       datetime.time(0, 10), datetime.time(0, 10), datetime.time(0, 10),
       datetime.time(0, 10), datetime.time(0, 10), datetime.time(0, 10),
       datetime.time(0, 10), datetime.time(0, 10), datetime.time(0, 10),
       datetime.time(0, 10), datetime.time(0, 10), datetime.time(0, 10)],
      dtype=object)

```

Note, here seconds and lower are not printed out because I got 0 of them, but are still taken in count.

You can also output to `date` with the associated timezone:

```python

>>> x.timetz

array([datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris')),
       datetime.time(0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris'))],
      dtype=object)

```

Now you can recreate the date as `datetime.datetime`.

```python

>>> datetime.combine(x.date[0], x.timetz[0])

datetime.datetime(2024, 1, 16, 0, 10, tzinfo=zoneinfo.ZoneInfo(key='Europe/Paris'))

```

And gracefully convert it back to `pd.Timestamp` without loss of time zone information.

```python

>>> pd.Timestamp(d)

Timestamp('2024-01-16 00:10:00+0100', tz='Europe/Paris')

```

Mental model:

**datetime.datetime**

- Python scalar date + time object
- general-purpose
- microsecond precision
- huge year range
- no vectorized array behavior

**pd.Timestamp**

- pandas scalar date + time object
- integrates with DatetimeIndex / Series
- nanosecond-oriented
- supports pd.NaT ecosystem
- strong timezone/time-series integration
- works with Timedelta and DateOffset

In `pandas`, work stays with `pd.Timestamp` as long as possible. Convert to Python `datetime` mostly for interoperability with libraries that expect standard Python objects.

Also, a quick point about the difference of type you see in `dtype` when you print out a `pd.DatetimeIndex`, and the actual `type(idx[0])` you see:

```python

>>> idx
DatetimeIndex(['2024-01-01 12:00:00+00:00', '2024-01-02 12:00:00+00:00',
               '2024-01-03 12:00:00+00:00'],
              dtype='datetime64[us, UTC]', freq='D')
>>> type(idx[0])
<class 'pandas.Timestamp'>

```

In fact, values are indeed stored as `datetime64[us, UTC]`, but when we take one value (a scalar), then `pandas` wrapps it into a richer scalar object, in this case a `pd.Timestamp`.

We have the equivalent with `numpy` here:

```python

>>> import numpy as np

>>> np.array([1, 2,3, 4], dtype="int64")

array([1, 2, 3, 4])

>>> np.array([1, 2,3, 4], dtype="int64")[0]

np.int64(1)

```

Back to methods.

You calso have basic `.floor(time_unit)` and `.ceil(time_unit)` methods.

Quick remainder:

- `floor` -> rounds value down to the nearest boundary

- `ceil` -> rounds value up to the nearest boundary

```python

>>> x.floor("h")

DatetimeIndex(['2024-01-16 00:00:00+01:00', '2024-01-23 00:00:00+01:00',
               '2024-01-30 00:00:00+01:00', '2024-02-06 00:00:00+01:00',
               '2024-02-13 00:00:00+01:00', '2024-02-20 00:00:00+01:00',
               '2024-02-27 00:00:00+01:00', '2024-03-05 00:00:00+01:00',
               '2024-03-12 00:00:00+01:00', '2024-03-19 00:00:00+01:00',
               '2024-03-26 00:00:00+01:00', '2024-04-02 00:00:00+02:00',
               '2024-04-09 00:00:00+02:00', '2024-04-16 00:00:00+02:00',
               '2024-04-23 00:00:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq=None)

>>> x.ceil("h")

DatetimeIndex(['2024-01-16 01:00:00+01:00', '2024-01-23 01:00:00+01:00',
               '2024-01-30 01:00:00+01:00', '2024-02-06 01:00:00+01:00',
               '2024-02-13 01:00:00+01:00', '2024-02-20 01:00:00+01:00',
               '2024-02-27 01:00:00+01:00', '2024-03-05 01:00:00+01:00',
               '2024-03-12 01:00:00+01:00', '2024-03-19 01:00:00+01:00',
               '2024-03-26 01:00:00+01:00', '2024-04-02 01:00:00+02:00',
               '2024-04-09 01:00:00+02:00', '2024-04-16 01:00:00+02:00',
               '2024-04-23 01:00:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq=None)

```

Those are also vectorized operations.

And in this case, `.round("h")` will have the same effect as `.floor("h")`.

```python

>>> x.round("h")

DatetimeIndex(['2024-01-16 00:00:00+01:00', '2024-01-23 00:00:00+01:00',
               '2024-01-30 00:00:00+01:00', '2024-02-06 00:00:00+01:00',
               '2024-02-13 00:00:00+01:00', '2024-02-20 00:00:00+01:00',
               '2024-02-27 00:00:00+01:00', '2024-03-05 00:00:00+01:00',
               '2024-03-12 00:00:00+01:00', '2024-03-19 00:00:00+01:00',
               '2024-03-26 00:00:00+01:00', '2024-04-02 00:00:00+02:00',
               '2024-04-09 00:00:00+02:00', '2024-04-16 00:00:00+02:00',
               '2024-04-23 00:00:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq=None)

```

And the `.normalize()` methods that keeps the date but set time to `00:00:00` has also same effect in this case.

```python

>>> x.normalize()

DatetimeIndex(['2024-01-16 00:00:00+01:00', '2024-01-23 00:00:00+01:00',
               '2024-01-30 00:00:00+01:00', '2024-02-06 00:00:00+01:00',
               '2024-02-13 00:00:00+01:00', '2024-02-20 00:00:00+01:00',
               '2024-02-27 00:00:00+01:00', '2024-03-05 00:00:00+01:00',
               '2024-03-12 00:00:00+01:00', '2024-03-19 00:00:00+01:00',
               '2024-03-26 00:00:00+01:00', '2024-04-02 00:00:00+02:00',
               '2024-04-09 00:00:00+02:00', '2024-04-16 00:00:00+02:00',
               '2024-04-23 00:00:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq=None)

```

Note that for all these 4 operations, `freq` is lost.

But speaking of `freq`, there is one method where it is usefull, `.shift(n)`.

It will shift all the datetime by `n * freq` (if `freq` is available).

```python

>>> x.shift(1)

DatetimeIndex(['2024-01-23 00:10:00+01:00', '2024-01-30 00:10:00+01:00',
               '2024-02-06 00:10:00+01:00', '2024-02-13 00:10:00+01:00',
               '2024-02-20 00:10:00+01:00', '2024-02-27 00:10:00+01:00',
               '2024-03-05 00:10:00+01:00', '2024-03-12 00:10:00+01:00',
               '2024-03-19 00:10:00+01:00', '2024-03-26 00:10:00+01:00',
               '2024-04-02 00:10:00+02:00', '2024-04-09 00:10:00+02:00',
               '2024-04-16 00:10:00+02:00', '2024-04-23 00:10:00+02:00',
               '2024-04-30 00:10:00+02:00'],
              dtype='datetime64[us, Europe/Paris]', freq='W-TUE')

```

Here it shifted dates by one week.

Nothing special happens at year start or end (January 1st is not always a Monday, it increases by one every normal year and by 2 for a leap year).

Now, the infamous `.strftime()`.

Wow, big mental model change here, now `"M"` is minute lol, `"min"` does not exists.

If you want seconds after epoch January 1st 1970, you do:

```python

>>> x.strftime("%s")

Index(['1705360200', '1705965000', '1706569800', '1707174600', '1707779400',
       '1708384200', '1708989000', '1709593800', '1710198600', '1710803400',
       '1711408200', '1712009400', '1712614200', '1713219000', '1713823800'],
      dtype='str')

```

`"%s"` is supported on many Unix/Linux/macOS systems, but it is not part of the standard Python `strftime` directives. On some platforms, especially Windows, it may not work as expected.

What's fun is that you can now convert it to `int64`, it can give unique ascending ids.

```python

>>> x.strftime("%s").astype("int64")

Index([1705360200, 1705965000, 1706569800, 1707174600, 1707779400, 1708384200,
       1708989000, 1709593800, 1710198600, 1710803400, 1711408200, 1712009400,
       1712614200, 1713219000, 1713823800],
      dtype='int64')

```

Common date format is:

```python

>>> x.strftime("%Y-%m-%d %H:%M:%S")

Index(['2024-01-16 00:10:00', '2024-01-23 00:10:00', '2024-01-30 00:10:00',
       '2024-02-06 00:10:00', '2024-02-13 00:10:00', '2024-02-20 00:10:00',
       '2024-02-27 00:10:00', '2024-03-05 00:10:00', '2024-03-12 00:10:00',
       '2024-03-19 00:10:00', '2024-03-26 00:10:00', '2024-04-02 00:10:00',
       '2024-04-09 00:10:00', '2024-04-16 00:10:00', '2024-04-23 00:10:00'],
      dtype='str')

```

Most important notations:

```python

%Y  4-digit year        2024
%y  2-digit year        24
%m  month number        01
%B  full month name     January
%b  short month name    Jan
%d  day of month        16
%A  full weekday name   Tuesday
%a  short weekday name  Tue
%H  hour 00-23          00
%I  hour 01-12          12
%p  AM/PM               AM
%M  minute              10
%S  second              00
%f  microsecond         000000
%z  UTC offset          +0100
%Z  timezone name       CET

```

Now we'll introduce `pd.PeriodIndex` because we'll speak about the convertion from `pd.DatetimeIndex` to `pd.PeriodIndex` with `.to_period(time_unit)` method.

So, basically:

```python

>>> idx

DatetimeIndex(['2024-01-01', '2024-02-12', '2024-03-06'], dtype='datetime64[us]', freq=None)

>>> idx.to_period("M")

PeriodIndex(['2024-01', '2024-02', '2024-03'], dtype='period[M]')

>>> idx.to_period("Q")

PeriodIndex(['2024Q1', '2024Q1', '2024Q1'], dtype='period[Q-DEC]')

...

```

So, now this is good for grouping by, for example.

Indeed, semantically `pd.PeriodIndex` represent time spans / calendar buckets.

The, a `pd.PeriodIndex` is not timezone-aware.

Note that, if you do not give argument as `time unit`, it tries to infere it.

```python

>>> idx

DatetimeIndex(['2024-01-01 00:00:00', '2024-01-01 12:00:00',
               '2024-01-02 00:00:00'],
              dtype='datetime64[us]', freq=None)

>>> idx.to_period()

PeriodIndex(['2024-01-01 00:00', '2024-01-01 12:00', '2024-01-02 00:00'], dtype='period[12h]')

```

But, it can fail.

A period stores an integer representing the datetime and the frequency.

Elements of a `pd.PeriodIndex` are `pd.Period` objects, not `pd.Timestamp`.

But they also accepts comparisons operator.

```python

>>> idx2[0] == idx2[1]
False

>>> idx2[0] < idx2[1]
True

```

But now be carefull, because the identity/type of a `pd.Period` is defined not only by its value but also by its frequency, naive freq comparisons will fail.

```python

>>> idx2 < pd.Period("2025-01-01")

```

--> Error

You have to put the matching freq for comparisons.

```python

>>> idx2 < pd.Period("2025-01-01", freq="D")

```

Also fails because `idx2` is a monthly freq (`"M"`).

```python

>>> idx2
PeriodIndex(['2024-01', '2024-02', '2024-03'], dtype='period[M]')

```

Then, this succeeds.

```python

>>> idx2 < pd.Period("2025-01-01", freq="M")
array([ True,  True,  True])

```

Or even:

```python

>>> idx2[0] < pd.Period("2025-01-01", freq="M")
True

```

But `pd.Period` are smaller than `pd.Timestamp`:

```python

>>> import sys

>>> sys.getsizeof(pd.Timestamp("2024-01-01", tz="Europe/Paris"))

120 # bytes

>>> sys.getsizeof(pd.Period("2024-01-01", freq="M"))

72 # bytes

```

But their respective container is the same size.

```python

>>> sys.getsizeof(idx) # DatetimeIndex
56

>>> sys.getsizeof(idx2) # PeriodIndex
56

```

We create `pd.PeriodIndex` with the `.period_range()` method:

```python

>>> pd.period_range("2024-01-01", periods = 15, freq = "M")
PeriodIndex(['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
             '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
             '2025-01', '2025-02', '2025-03'],
            dtype='period[M]')

```

A `pd.Period` can be converted to a `pd.Timestamp` with `.to_timestamp()`.

Scalar.

```python

>>> idx2[0].to_timestamp()
Timestamp('2024-01-01 00:00:00')

```

Vectorized -> `pd.DatetimeIndex`

```python

>>> idx2.to_timestamp()
DatetimeIndex(['2024-01-01', '2024-02-01', '2024-03-01'], dtype='datetime64[us]', freq='MS')

```

You can also convert the `pd.DatetimeIndex` to a numpy array of standard `datetime.datetime` elements.

```python

>>> idx.to_pydatetime()
array([datetime.datetime(2024, 1, 1, 0, 0),
       datetime.datetime(2024, 2, 12, 0, 0),
       datetime.datetime(2024, 3, 6, 0, 0)], dtype=object)

```

So convertions work on scalar but also on their direct container.

I restate it but `datetime.datetime` are extremely small compared to their pandas counter part (especially `pd.DatetimeIndex`):

```python

>>> sys.getsizeof(datetime.datetime(2024, 3, 6))
48

```

Now, time to speak about Julian Date system.

```python

>>> idx = pd.DatetimeIndex([
...     "2024-01-01 00:00:00",
...     "2024-01-01 12:00:00",
...     "2024-01-02 00:00:00",
... ])

>>> jd = idx.to_julian_date()

>>> jd
Index([2460310.5, 2460311.0, 2460311.5], dtype='float64')

```

It converts each date into a floating point.

The `0` value / origin date is **4713 BC**.

One day is **1 unit**.

Notice the `.5` at midnight. 

That's because astronomical **Julian days start at noon**, not midnight.

It converts timestamps to a continuous astronomical day number (Julian Date System)

About Julian **calendar**:

The Julian calendar came first. It was introduced by Julius Caesar in 45 BC.

The Gregorian calendar came much later. It was introduced by Pope Gregory XIII in 1582 to correct the drift that had accumulated under the Julian calendar.

Why they differe ?

Because the Julian year is slightly too long:

```

Julian year:      365.25 days
Tropical year:    about 365.2422 days
Difference:       about 11 minutes per year

```

That small error accumulates.

Roughly:

```

1 day of drift every ~128 years

```

So over centuries, the Julian calendar falls behind the Gregorian calendar.

Example today

In the 20th and 21st centuries, the difference is 13 days.

So:

```

Gregorian: 2024-01-01
Julian:    2023-12-19

```

They are the same physical day, but expressed in two different calendars.


- Final Cheat Sheet:

```python

# components
idx.year
idx.month
idx.day
idx.hour
idx.minute
idx.second
idx.dayofweek
idx.dayofyear
idx.quarter
idx.days_in_month

# flags
idx.is_month_start
idx.is_month_end
idx.is_quarter_start
idx.is_quarter_end
idx.is_year_start
idx.is_year_end
idx.is_leap_year

# names / Python objects
idx.day_name()
idx.month_name()
idx.date
idx.time
idx.timetz

# timezone
idx.tz # the timzeone
idx.tz_localize(...)
idx.tz_convert(...)

# rounding / shifting
idx.floor(...)
idx.ceil(...)
idx.round(...)
idx.normalize()
idx.shift(...)

# conversion
idx.strftime(...)
idx.to_period(...)
idx.to_pydatetime()
idx.to_julian_date()

# frequency
idx.freq
idx.freqstr
idx.inferred_freq

```

### Custom `DatetimeRangeSr` class

That's just a Proof Of Concept of what a `DatetimeRangeIndex` with a `pd.Series` could be.

The chosen design is just a class wrapper, because even if we can assign other type to the index of a  `pd.Series`, like a list.

```python

>>> x = pd.Series([1,2,3])

>>> x.index

RangeIndex(start=0, stop=3, step=1)

>>> x.index = [1,2,13]

>>> x
1     1
2     2
13    3
dtype: int64

```

Modifying the behavior of the different dataframe operations with a brand new index type forces me to look at `pandas` code direclty, and I do not have the motivation to do so.

So here's my class wrapper.

We'll discuss constructor API design, and why this one is awfull in a **data-first** POV.

```python

import pandas as pd
from typing import Self
import numpy as np

class DatetimeRangeSr:
    def __init__(
        self,
        sr: pd.Series,
        metadata: tuple[pd.Timestamp, pd.Timestamp, pd.Timedelta],
    ):
        start, stop, step = metadata

        if not isinstance(start, pd.Timestamp):
            start = pd.Timestamp(start)

        if not isinstance(stop, pd.Timestamp):
            stop = pd.Timestamp(stop)

        if not isinstance(step, pd.Timedelta):
            step = pd.Timedelta(step)

        if step <= pd.Timedelta(0):
            raise ValueError("step must be positive")

        if not start < stop:
            raise ValueError("stop must be higher than start")

        expected_len = (stop - start) // step

        if start + expected_len * step != stop:
            raise ValueError("stop must align exactly with start + n * step")

        if len(sr) != expected_len:
            raise ValueError(
                f"Series length does not match datetime range: "
                f"len(sr)={len(sr)}, expected={expected_len}"
            )

        self.sr = sr.reset_index(drop=True)
        self.start = start
        self.stop = stop
        self.step = step
        self.length = int(expected_len)

    def __len__(self):
        return self.length

    def __repr__(self):
        return (
            f"DatetimeRangeSr("
            f"start={self.start!r}, "
            f"stop={self.stop!r}, "
            f"step={self.step!r}, "
            f"length={self.length}"
            f")\n"
            f"{self.sr}"
        )

    def datetime_at(self, i: int) -> pd.Timestamp:
        if i < 0:
            i += self.length

        if i < 0 or i >= self.length:
            raise IndexError("index out of bounds")

        return self.start + i * self.step

    def position_of(self, date: pd.Timestamp) -> int:
        date = pd.Timestamp(date)

        if date < self.start or date >= self.stop:
            raise KeyError("date out of bounds")

        delta = date - self.start

        if delta % self.step != pd.Timedelta(0):
            raise KeyError("date does not match the DatetimeRangeSr step")

        return int(delta // self.step)

    def __getitem__(self, key):

        if isinstance(key, int):
            return self.sr.iloc[key]

        if isinstance(key, slice):
            if isinstance(key.start, int):
                return self.sr.iloc[key]
            else:
                return self._getitem_slice(key)

        date = pd.Timestamp(key)
        idx = self.position_of(date)
        return self.sr.iloc[idx]


    def _normalize_slice(self, key: slice) -> slice:
        if (
            (key.start is None)
            and (key.stop is None)
            and (key.step is None)
        ):
            return key

        if key.start is None:
            start_pos = 0
        else:
            start_pos = self.position_of(pd.Timestamp(key.start))

        if key.stop is None:
            stop_pos = self.length
        else:
            stop = pd.Timestamp(key.stop)

            if stop > self.stop:
                raise ValueError("stop out of bounds")
            elif stop == self.stop:
                stop_pos = self.length
            else:
                stop_pos = self.position_of(stop)

        if key.step is None:
            slice_step = 1
        elif isinstance(key.step, int):
            slice_step = key.step
        else:
            step = pd.Timedelta(key.step)

            if step <= pd.Timedelta(0):
                raise ValueError("slice step must be positive")

            if step % self.step != pd.Timedelta(0):
                raise ValueError("slice step must be a multiple of the range step")

            slice_step = int(step // self.step)

        return slice(start_pos, stop_pos, slice_step)

    def _getitem_slice(self, key: slice) -> Self:

        key = self._normalize_slice(key)

        start_pos, stop_pos, slice_step = key.indices(self.length)

        if slice_step <= 0:
            raise ValueError("negative or zero slice steps are not supported yet")

        new_sr = self.sr.iloc[key].reset_index(drop=True)

        new_start = self.datetime_at(start_pos)
        new_step = self.step * slice_step
        new_stop = new_start + len(new_sr) * new_step

        return DatetimeRangeSr(
            new_sr,
            metadata=(new_start, new_stop, new_step),
        )

    def to_series_with_datetime_index(self) -> pd.Series:
        idx = pd.date_range(
            start=self.start,
            periods=self.length,
            freq=self.step,
        )

        return pd.Series(self.sr.to_numpy(), index=idx, name=self.sr.name)

    def concat(self, objects: list[Self]) -> Self:
        all_objects = [self] + objects
    
        step = self.step
    
        for obj in all_objects:
            if obj.step != step:
                raise ValueError("cannot concat: all ranges must have the same step")
    
        for a, b in zip(all_objects, all_objects[1:]):
            if a.stop != b.start:
                raise ValueError(
                    "cannot concat: ranges are not contiguous "
                    f"between {a.stop} and {b.start}"
                )
    
        new_sr = pd.concat(
            [obj.sr for obj in all_objects],
            ignore_index=True,
        )
    
        return type(self)(
            new_sr,
            metadata=(self.start, all_objects[-1].stop, step),
        )

    def _lower_bound_pos(self, other: pd.Timestamp) -> int:
        if other <= self.start:
            return 0
    
        if other > self.stop:
            return self.length
    
        delta = other - self.start
        q = delta // self.step
        r = delta % self.step
    
        if r == pd.Timedelta(0):
            return int(q)
    
        return int(q) + 1
    
    
    def _upper_bound_pos(self, other: pd.Timestamp) -> int:
        if other < self.start:
            return 0
    
        if other >= self.stop:
            return self.length
    
        delta = other - self.start
        q = delta // self.step
        r = delta % self.step
    
        return int(q) + 1
    
    
    def _compare_datetime(self, other, op: str):
        other = pd.Timestamp(other)
    
        values = np.zeros(self.length, dtype=bool)
    
        lb = self._lower_bound_pos(other)
        ub = self._upper_bound_pos(other)
    
        match op:
            case "<":
                values[:lb] = True
            case "<=":
                values[:ub] = True
            case ">":
                values[ub:] = True
            case ">=":
                values[lb:] = True
            case "==":
                values[lb:ub] = True
            case "!=":
                values[:] = True
                values[lb:ub] = False
            case _:
                raise ValueError(f"unknown comparison operator: {op}")
    
        return values

    def __lt__(self, other):
        return self._compare_datetime(other, "<")

    def __le__(self, other):
        return self._compare_datetime(other, "<=")
    
    def __eq__(self, other):
        return self._compare_datetime(other, "==")
    
    def __ne__(self, other):
        return self._compare_datetime(other, "!=")
    
    def __ge__(self, other):
        return self._compare_datetime(other, ">=")
    
    def __gt__(self, other):
        return self._compare_datetime(other, ">")
```

Simple enough.

It respects the stop-excluding pyton range semantic.

Len is of course `(stop - start) // step`.

We redifine operation like len:

```python

def __len__(self):
    return self.length

```
Print.

```python

def __repr__(self):
    return (
        f"DatetimeRangeSr("
        f"start={self.start!r}, "
        f"stop={self.stop!r}, "
        f"step={self.step!r}, "
        f"length={self.length}"
        f")\n"
        f"{self.sr}"
    )

```

Random access, suporting slice.

```python

def __getitem__(self, key):
    if isinstance(key, int):
        return self.sr.iloc[key]

    if isinstance(key, slice):
        if isinstance(key.start, int):
            return self.sr.iloc[key]
        else:
            return self._getitem_slice(key)

    date = pd.Timestamp(key)
    idx = self.position_of(date)
    return self.sr.iloc[idx]

```

Note that it of course accepts both direct `iloc` with `int`, and also `loc` by first converting to a the corresponding index (`self.position_of(date)`) (just one corresponding `idx` because monotonicly increasing date) and then performing `iloc`.

Here the convertion from `pd.Timestamp` to `int`:

```python

def position_of(self, date: pd.Timestamp) -> int:
    date = pd.Timestamp(date)

    if date < self.start or date >= self.stop:
        raise KeyError("date out of bounds")

    delta = date - self.start

    if delta % self.step != pd.Timedelta(0):
        raise KeyError("date does not match the DatetimeRangeSr step")

    return int(delta // self.step)

```

Note that there is no rounding or so, if the datetime range does not correspond to a true range, then error:

```python

if delta % self.step != pd.Timedelta(0):
    raise KeyError("date does not match the DatetimeRangeSr step")

```

You also note that in random access, I check wether it is done with slice with `isinstance(key, slice)`, if it is true then we pass to the slice random access function.

Note that a slice is `start:end:step` -> `slice(start, end, range)`.

Those are slices.

- `1:4:2` -> start is `1`, end is `4` (stop excluding) and step is `2`

- `:4:1` -> start is `None` -> `0`, end is `4` (stop excluding) and step is `1`

- `1:` -> start is `1`, step is `None` -> defaults to `1`, end is `None` -> length of he object


```python

def _getitem_slice(self, key: slice) -> Self:

    key = self._normalize_slice(key)

    start_pos, stop_pos, slice_step = key.indices(self.length)

    if slice_step <= 0:
        raise ValueError("negative or zero slice steps are not supported yet")

    new_sr = self.sr.iloc[key].reset_index(drop=True)

    new_start = self.datetime_at(start_pos)
    new_step = self.step * slice_step
    new_stop = new_start + len(new_sr) * new_step

    return DatetimeRangeSr(
        new_sr,
        metadata=(new_start, new_stop, new_step),
    )

```

It's of course another semantic meaning than scalar random access, here I return a brand new `DatetimeRangeSr`, so I need to construct a start, an end date and also a step timedelta.

`.datetime_at()` method will help us for that.

```python

def datetime_at(self, i: int) -> pd.Timestamp:
    if i < 0:
        i += self.length
 
    if i < 0 or i >= self.length:
        raise IndexError("index out of bounds")
 
    return self.start + i * self.step

```

In fact I do in the following order: slice -> normalize to `int` indices with `_normalize_slice` and then use `datetime_at` to get the intended value for the metadata.

So, what's going on when the class is sliced with `pd.Datetime` instead of `int` ?

Here is `_normalize_slice()` method that will compute the indices for constructing the new object.

```python

def _normalize_slice(self, key: slice) -> slice:
    if (
        (key.start is None)
        and (key.stop is None)
        and (key.step is None)
    ):
        return key

    if key.start is None:
        start_pos = 0
    else:
        start_pos = self.position_of(pd.Timestamp(key.start))

    if key.stop is None:
        stop_pos = self.length
    else:
        stop = pd.Timestamp(key.stop)

        if stop > self.stop:
            raise ValueError("stop out of bounds")
        elif stop == self.stop:
            stop_pos = self.length
        else:
            stop_pos = self.position_of(stop)

    if key.step is None:
        slice_step = 1
    elif isinstance(key.step, int):
        slice_step = key.step
    else:
        step = pd.Timedelta(key.step)

        if step <= pd.Timedelta(0):
            raise ValueError("slice step must be positive")

        if step % self.step != pd.Timedelta(0):
            raise ValueError("slice step must be a multiple of the range step")

        slice_step = int(step // self.step)

    return slice(start_pos, stop_pos, slice_step)

```

Of course, I define what are comparisons operator:

```python

def __lt__(self, other):
    return self._compare_datetime(other, "<")

def __le__(self, other):
    return self._compare_datetime(other, "<=")

def __eq__(self, other):
    return self._compare_datetime(other, "==")

def __ne__(self, other):
    return self._compare_datetime(other, "!=")

def __ge__(self, other):
    return self._compare_datetime(other, ">=")

def __gt__(self, other):
    return self._compare_datetime(other, ">")

```

-> less than, less or equal, equal, not equal, greater or equal, greater than

Now here the dispatcher and operator logic.

```python

def _compare_datetime(self, other, op: str):
    other = pd.Timestamp(other)

    values = np.zeros(self.length, dtype=bool)

    lb = self._lower_bound_pos(other)
    ub = self._upper_bound_pos(other)

    match op:
        case "<":
            values[:lb] = True
        case "<=":
            values[:ub] = True
        case ">":
            values[ub:] = True
        case ">=":
            values[lb:] = True
        case "==":
            values[lb:ub] = True
        case "!=":
            values[:] = True
            values[lb:ub] = False
        case _:
            raise ValueError(f"unknown comparison operator: {op}")

    return values

```

Note: because I already know `step`, `start` and stop date, I can just pre allocate a N length numpy boolean array, and after; partially set boolean values where I need.

Where I need is using upper and lower bounds.

Lower bound:

```python

def _lower_bound_pos(self, other: pd.Timestamp) -> int:
    if other <= self.start:
        return 0

    if other > self.stop:
        return self.length

    delta = other - self.start
    q = delta // self.step
    r = delta % self.step

    if r == pd.Timedelta(0):
        return int(q)

    return int(q) + 1

```

Higher bound:

```python

def _upper_bound_pos(self, other: pd.Timestamp) -> int:
    if other < self.start:
        return 0

    if other >= self.stop:
        return self.length

    delta = other - self.start
    q = delta // self.step
    r = delta % self.step

    return int(q) + 1

```

So lower bound is `Date_n` and upper bound is `Date_n+1`

For `==` and `!=`, the boolean operation is only effective if we got a true inequality or equality.

Only when `LowerBound + 1 = UpperBound`.

But when `Other` is not perfectly equal to `Date_Start + n * Step`, then we got `LowerBound == UpperBound`, then no assigment possible.

Example:

```python

>>> lst = np.zeros(3, dtype=bool) # creates a numpy array of 3 boolean elements

>>> lst

array([False, False, False])

>>> lst[1:1] = True

>>> lst

array([False, False, False])

```

Because `lst[n:n] == []`.

Btw, those slice assigments differe from normal list assigment.

With `numpy.array`, this is possible:

```python

>>> lst
array([False, False, False])

>>> lst[0:] = True

>>> lst
array([ True,  True,  True])

```

And the equivalent in raw lists is:

```python

>>> lst2 = [False, False, False]

>>> lst2[0:] = [True] * len(lst2)

>>> lst2
[True, True, True]

```

So the list slice assigment has more overhead because it expects an iterable, and this iterable requires to create a temporary list whereas the `numpy` version understands the previous code as broadcasting the value to all the elements of the containers selected by the slice.

Look what happen if the assigment **iterable** is not the same length of the assigned iterable.

```python

>>> lst2[0:] = [True] * 2

>>> lst2
[True, True]

```

That's right, the assigned iterable shape is dictated by the shape of the value we assign from.

```python

>>> lst2 = [False] * 5

>>> lst2[1:] = [True] * 2

>>> lst2
[False, True, True]

```

```python

>>> lst2
[False, False, False, False, False]

>>> lst2[:3] = [True] * 2

>>> lst2
[True, True, False, False]

```

How to use it ?

Constructor.

```python

ser = pd.Series([10, 20, 30, 22, 56])

drs = DatetimeRangeSr(
    ser,
    metadata=(
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-06"),
        pd.Timedelta(days=1),
    ),
)

```

Random access and slices.

```python

print(drs[1])

```

Output.

```

20

```

```python

print(drs[1::2])

```

Output.

```

DatetimeRangeSr(start=Timestamp('2024-01-02 00:00:00'), stop=Timestamp('2024-01-06 00:00:00'), step=Timedelta('2 days 00:00:00'), length=2)
0    20
1    22
dtype: int64

```

```python

print(drs[pd.Timestamp("2024-01-02"):pd.Timestamp("2024-01-05")])

```

Output.

```

DatetimeRangeSr(start=Timestamp('2024-01-02 00:00:00'), stop=Timestamp('2024-01-05 00:00:00'), step=Timedelta('1 days 00:00:00'), length=3)
0    20
1    30
2    22
dtype: int64

```

Comparison operations.

```python

print(drs > pd.Timestamp("2024-01-03"))

```

Output.

```

[False False False  True  True]

```

Concatenation (vertical).

```python

ser2 = pd.Series([10, 20, 30, 22, 56] * 2)

drs2 = DatetimeRangeSr(
    ser2,
    metadata=(
        pd.Timestamp("2024-01-06"),
        pd.Timestamp("2024-01-16"),
        pd.Timedelta(days=1),
    ),
)

print(drs.concat([drs2]))

```

Output.

```

DatetimeRangeSr(start=Timestamp('2024-01-01 00:00:00'), stop=Timestamp('2024-01-16 00:00:00'), step=Timedelta('1 days 00:00:00'), length=15)
0     10
1     20
2     30
3     22
4     56
5     10
6     20
7     30
8     22
9     56
10    10
11    20
12    30
13    22
14    56
dtype: int64

```

And finaly the convertions to a `pd.Series` with a `pd.DatetimeIndex`:

```python

x = drs.to_series_with_datetime_index()

print(x)

print("###")

print(type(x.index))

```

Output.

```python

2024-01-01    10
2024-01-02    20
2024-01-03    30
2024-01-04    22
2024-01-05    56
Freq: 24h, dtype: int64
###
<class 'pandas.DatetimeIndex'>

```

Note that all internal implementations that should not be accessible to the user begins with an underscore.

This is also the case for `pd.Series`, we have for example `.values` attribute, but also the internal `._values` attribute that should not be accessed.

```python

>>> x = pd.Series([1, 2, 3, 4])

>>> x.values
array([1, 2, 3, 4])

>>> x._values
array([1, 2, 3, 4])

```

### `pd.PeriodIndex`

We already talked about it in [#`pd.DatetimeIndex`](#`pd.DatetimeIndex`) section.

### `pd.TimedeltaIndex`

It represents elapsed time from an event.

Here its constructor:

```python

>>> idx = pd.TimedeltaIndex(["1 days 00:00:00", 
                             "2 days 00:00:00", 
                             "3 days 00:00:00"], 
                             freq=None, 
                             dtype="timedelta64[ns]")

>>> idx
TimedeltaIndex(['1 days', '2 days', '3 days'], dtype='timedelta64[ns]', freq=None)

```

With tis notation `N date time`.

Or more traditionally:

```python

>>> idx2 = pd.TimedeltaIndex([pd.Timedelta(days=1), 
                              pd.Timedelta(days=2), 
                              pd.Timedelta(days=3)], 
                              freq=None, 
                              dtype="timedelta64[ns]")

>>> idx2
TimedeltaIndex(['1 days', '2 days', '3 days'], dtype='timedelta64[ns]', freq='D')

```

Of course here I could have put `"D"` as the frequency, anyway I can retrieve it via inferring it.

```python

>>> idx2.inferred_freq
'D'

```

Btw, in the same way we create a `pd.Timedelta` by operating on 2 `pd.Timestamp` (like a substraction), we can create a `pd.TimedeltaIndex` by operating on a `pd.DatetimeIndex`.

```python

>>> pd.date_range("2024-01-01", periods=67, freq="D") - pd.Timestamp("2024-01-05")
TimedeltaIndex(['-4 days', '-3 days', '-2 days', '-1 days',  '0 days',
                 '1 days',  '2 days',  '3 days',  '4 days',  '5 days',
                 '6 days',  '7 days',  '8 days',  '9 days', '10 days',
                '11 days', '12 days', '13 days', '14 days', '15 days',
                '16 days', '17 days', '18 days', '19 days', '20 days',
                '21 days', '22 days', '23 days', '24 days', '25 days',
                '26 days', '27 days', '28 days', '29 days', '30 days',
                '31 days', '32 days', '33 days', '34 days', '35 days',
                '36 days', '37 days', '38 days', '39 days', '40 days',
                '41 days', '42 days', '43 days', '44 days', '45 days',
                '46 days', '47 days', '48 days', '49 days', '50 days',
                '51 days', '52 days', '53 days', '54 days', '55 days',
                '56 days', '57 days', '58 days', '59 days', '60 days',
                '61 days', '62 days'],
               dtype='timedelta64[us]', freq='D')

```

You note that `timedelta64[us]` is the type for the array storage while `pd.Timedelta` is the equivalent scalar type.

There is also great interoperability with `numpy`:

```python

>>> pd.Timedelta(np.timedelta64(5, "us"))
Timedelta('0 days 00:00:00.000005')

>>> pd.Timedelta(np.timedelta64(5, "ns"))
Timedelta('0 days 00:00:00.000000005')

```

The unit of a `pd.Timedelta` and by extension of a `timedelta64[...]` can change based on the chosen frequency:

```python

>>> x = pd.date_range("2024-01-01", periods = 15, freq = "ns") - pd.Timestamp("2024-01-01")

>>> x
TimedeltaIndex([          '0 days 00:00:00', '0 days 00:00:00.000000001',
                '0 days 00:00:00.000000002', '0 days 00:00:00.000000003',
                '0 days 00:00:00.000000004', '0 days 00:00:00.000000005',
                '0 days 00:00:00.000000006', '0 days 00:00:00.000000007',
                '0 days 00:00:00.000000008', '0 days 00:00:00.000000009',
                '0 days 00:00:00.000000010', '0 days 00:00:00.000000011',
                '0 days 00:00:00.000000012', '0 days 00:00:00.000000013',
                '0 days 00:00:00.000000014'],
               dtype='timedelta64[ns]', freq='ns')

```

It supports:

```

"s"   # seconds
"ms"  # milliseconds
"us"  # microseconds
"ns"  # nanoseconds

```

Of course, the same goes for `datetime64[...]`:

```python

>>> x = pd.date_range("2024-01-01", periods = 15, freq = "ns")

>>> x
DatetimeIndex([          '2024-01-01 00:00:00',
               '2024-01-01 00:00:00.000000001',
               '2024-01-01 00:00:00.000000002',
               '2024-01-01 00:00:00.000000003',
               '2024-01-01 00:00:00.000000004',
               '2024-01-01 00:00:00.000000005',
               '2024-01-01 00:00:00.000000006',
               '2024-01-01 00:00:00.000000007',
               '2024-01-01 00:00:00.000000008',
               '2024-01-01 00:00:00.000000009',
               '2024-01-01 00:00:00.000000010',
               '2024-01-01 00:00:00.000000011',
               '2024-01-01 00:00:00.000000012',
               '2024-01-01 00:00:00.000000013',
               '2024-01-01 00:00:00.000000014'],
              dtype='datetime64[ns]', freq='ns')

```

Because the underneath type is a `int64`, so there is a tradeoff while choosing the unit, `timedelta64["s"]` for example will cover a much wider range than `timedelta64["ns"]` but be less accurate.

This is stored as a signed int 64 type because `timedelta` can be negatives, for example:

```python

>>> x = pd.date_range("2024-01-01", periods = 15, freq = "s") - pd.Timestamp("2025-01-01")

>>> x
TimedeltaIndex(['-366 days +00:00:00', '-366 days +00:00:01',
                '-366 days +00:00:02', '-366 days +00:00:03',
                '-366 days +00:00:04', '-366 days +00:00:05',
                '-366 days +00:00:06', '-366 days +00:00:07',
                '-366 days +00:00:08', '-366 days +00:00:09',
                '-366 days +00:00:10', '-366 days +00:00:11',
                '-366 days +00:00:12', '-366 days +00:00:13',
                '-366 days +00:00:14'],
               dtype='timedelta64[us]', freq='s')

>>> x.asi8
array([-31622400000000, -31622399000000, -31622398000000, -31622397000000,
       -31622396000000, -31622395000000, -31622394000000, -31622393000000,
       -31622392000000, -31622391000000, -31622390000000, -31622389000000,
       -31622388000000, -31622387000000, -31622386000000])

```

`.asi8` is the attribute storin the integer values for all those `timedelta64`.

The same goes for `datetime64` for the date before the year `1970`, we can inspect the integer value by also grabbing the `.asi8` attribute:

```python

>>> x = pd.date_range("1024-01-01", periods = 15, freq = "s")

>>> x
DatetimeIndex(['1024-01-01 00:00:00', '1024-01-01 00:00:01',
               '1024-01-01 00:00:02', '1024-01-01 00:00:03',
               '1024-01-01 00:00:04', '1024-01-01 00:00:05',
               '1024-01-01 00:00:06', '1024-01-01 00:00:07',
               '1024-01-01 00:00:08', '1024-01-01 00:00:09',
               '1024-01-01 00:00:10', '1024-01-01 00:00:11',
               '1024-01-01 00:00:12', '1024-01-01 00:00:13',
               '1024-01-01 00:00:14'],
              dtype='datetime64[us]', freq='s')

>>> x.asi8
array([-29852928000000000, -29852927999000000, -29852927998000000,
       -29852927997000000, -29852927996000000, -29852927995000000,
       -29852927994000000, -29852927993000000, -29852927992000000,
       -29852927991000000, -29852927990000000, -29852927989000000,
       -29852927988000000, -29852927987000000, -29852927986000000])

```

The equivalent to `pd.date_range(...)` constructor for `pd.DatetimeIndex`, is `pd.timedelta_range(...)` for constructing `pd.TimedeltaIndex`.

```python

>>> pd.timedelta_range(start="0 days", periods=4, freq="5h")
TimedeltaIndex(['0 days 00:00:00', '0 days 05:00:00', '0 days 10:00:00',
                '0 days 15:00:00'],
               dtype='timedelta64[us]', freq='5h')

```

Or:

```python

>>> pd.timedelta_range(start=pd.Timedelta(days=1), periods=4, freq="5h")
TimedeltaIndex(['1 days 00:00:00', '1 days 05:00:00', '1 days 10:00:00',
                '1 days 15:00:00'],
               dtype='timedelta64[us]', freq='5h')

```

Of course comparions to other `pd.Timedelta` work.

```python

>>> idx
TimedeltaIndex(['1 days', '2 days', '3 days'], dtype='timedelta64[ns]', freq='D')

>>> idx < pd.Timedelta(minutes=1)
array([False, False, False])

```

I can also construct it directly via the `.to_timedelta()` method.

```python

>>> pd.to_timedelta([1, 2, 3], unit="D")
TimedeltaIndex(['1 days', '2 days', '3 days'], dtype='timedelta64[s]', freq="D")

```

I restate here, but note the `dtype` **does not** affect the size of the Container neither the elements.

Container size stays the same.

```python

>>> idx=pd.TimedeltaIndex([pd.Timedelta(days=1), 
                           pd.Timedelta(days=2), 
                           pd.Timedelta(days=3)], 
                           freq="D", 
                           dtype="timedelta64[us]")

>>> idx.memory_usage(deep=True)
24 # 3 * 8 bytes

>>> idx=pd.TimedeltaIndex([pd.Timedelta(days=1), 
                           pd.Timedelta(days=2), 
                           pd.Timedelta(days=3)], 
                           freq="D", 
                           dtype="timedelta64[s]")

>>> idx.memory_usage(deep=True)
24

>>> idx=pd.TimedeltaIndex([pd.Timedelta(days=1), 
                           pd.Timedelta(days=2), 
                           pd.Timedelta(days=3)], 
                           freq="D", 
                           dtype="timedelta64[ns]")

>>> idx.memory_usage(deep=True)
24

```

Same for elements, still `pd.Timedelta` -> same size.

```python

>>> idx=pd.TimedeltaIndex([pd.Timedelta(days=1), pd.Timedelta(days=2), pd.Timedelta(days=3)], freq="D", dtype="timedelta64[ns]")
>>> sys.getsizeof(idx[0])
160

>>> idx=pd.TimedeltaIndex([pd.Timedelta(days=1), pd.Timedelta(days=2), pd.Timedelta(days=3)], freq="D", dtype="timedelta64[us]")
>>> sys.getsizeof(idx[0])
160

>>> idx=pd.TimedeltaIndex([pd.Timedelta(days=1), pd.Timedelta(days=2), pd.Timedelta(days=3)], freq="D", dtype="timedelta64[s]")
>>> sys.getsizeof(idx[0])
160

```

We also note that the `pd.Timedelta` object is 40 bytes larger than `pd.Timestamp`:

```python

>>> x = pd.DatetimeIndex([pd.Timestamp("2024-01-01")], dtype = "datetime64[us]")

>>> sys.getsizeof(x[0])

120

>>> x1 = pd.TimedeltaIndex([pd.Timedelta(3)], freq = "D", dtype = "timedelta64[us]")

>>> sys.getsizeof(x1[0])

160

```

For standard  `pd.Index`, you have a wide amount of `dtypes` to have more control on the range, size and precision of your indices with `numpy` types:

```python

>>> sys.getsizeof(pd.Index([1, 2, 3, 4], dtype = np.int32)[0])
28

>>> sys.getsizeof(pd.Index([1, 2, 3, 4], dtype = np.int16)[0])
26

>>> sys.getsizeof(pd.Index([1, 2, 3, 4], dtype = np.int8)[0])
25

>>> sys.getsizeof(pd.Index([1, 2, 3, 4], dtype = np.int64)[0])
32

>>> sys.getsizeof(pd.Index([1, 2, 3, 4], dtype = np.uint64)[0])
32

```

### Custom `TimedeltaRangeSr`

Yess, same as `pd.DatetimeRangeSr`, here is a POC of what could be a `pd.TimedeltaRangeSr`.

Here some snippets that will make you understand the implementation.

First, you must understand that when an array contains elements that are normally part of an Index container type and that this numpy array is passed as `index` for a `pandas.Series`, then the index container type is direclty inferred.

```python

>>> step = pd.Timedelta(days=1.3)

>>> pd.Series([1] * 5, index = np.array([ step * i for i in range(5) ])).index
TimedeltaIndex(['0 days 00:00:00', '1 days 07:12:00', '2 days 14:24:00',
                '3 days 21:36:00', '5 days 04:48:00'],
               dtype='timedelta64[us]', freq=None)

```

This is fundamental, because here I implemented the convertion to a `pd.Series` with a `pd.TimedeltaIndex` as follow:

```python

def to_series_with_timedelta_index(self) -> pd.Series:
    idx = np.array([ self.start + self.step * i for i in range(self.length) ])

    return pd.Series(self.sr.to_numpy(), index=idx, name=self.sr.name)

```

Just for educational purposes.

Contrary to the more formal constructor I used with `DatetimeRangeSr`:

```python

def to_series_with_datetime_index(self) -> pd.Series:
    idx = pd.date_range(
        start=self.start,
        periods=self.length,
        freq=self.step,
    )

    return pd.Series(self.sr.to_numpy(), index=idx, name=self.sr.name)

```

Here is the complete implementation.

```python

import pandas as pd
from typing import Self
import numpy as np

class TimedeltaRangeSr:
    def __init__(
        self,
        sr: pd.Series,
        metadata: tuple[pd.Timedelta, str, pd.Timedelta],
    ):
        start, unit, step = metadata

        if not isinstance(start, pd.Timedelta):
            start = pd.to_timedelta(start, unit=unit)

        if not isinstance(step, pd.Timedelta):
            step = pd.to_timedelta(step, unit=unit)

        period = len(sr)

        self.sr = sr.reset_index(drop=True)
        self.start = start
        self.period = period
        self.unit = unit
        self.step = step
        self.stop = start + period * step
        self.length = period

    def __len__(self):
        return self.length

    def __repr__(self):
        return (
            f"TimedeltaRangeSr("
            f"start={self.start!r}, "
            f"stop={self.stop!r}, "
            f"period={self.period!r}, "
            f"unit={self.unit!r}, "
            f"step={self.step!r}, "
            f"length={self.length}"
            f")\n"
            f"{self.sr}"
        )

    def timedelta_at(self, i: int) -> pd.Timedelta:
        if i < 0:
            i += self.length

        if i < 0 or i >= self.length:
            raise IndexError("index out of bounds")

        return self.start + i * self.step

    def position_of(self, time: pd.Timedelta) -> int:

        if not isinstance(time, pd.Timedelta):
            time = pd.to_timedelta(time, unit=self.unit)

        if time < self.start or time >= self.stop:
            raise KeyError("date out of bounds")

        delta = time - self.start

        if delta % self.step != pd.Timedelta(0):
            raise KeyError("date does not match the TimedeltaRangeSr step")

        return int(delta // self.step)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.sr.iloc[key]

        if isinstance(key, slice):
            if isinstance(key.start, int):
                return self.sr.iloc[key]
            else:
                return self._getitem_slice(key)

        if not isinstance(key, pd.Timedelta):
            key = pd.to_timedelta(key, unit=unit)

        idx = self.position_of(key)
        return self.sr.iloc[idx]


    def _normalize_slice(self, key: slice) -> slice:

        if (
            (key.start is None)
            and (key.stop is None)
            and (key.step is None)
        ):
            return key

        if key.start is None:
            start_pos = 0
        else:
            start_pos = self.position_of(pd.to_timedelta(key.start))

        if key.stop is None:
            stop_pos = self.length
        else:
            stop = pd.to_timedelta(key.stop)

            if stop > self.stop:
                raise ValueError("stop out of bounds")
            elif stop == self.stop:
                stop_pos = self.length
            else:
                stop_pos = self.position_of(stop)

        if key.step is None:
            slice_step = 1
        elif isinstance(key.step, int):
            slice_step = key.step
        else:
            step = pd.to_timedelta(key.step)

            if step <= pd.Timedelta(0):
                raise ValueError("slice step must be positive")

            if step % self.step != pd.Timedelta(0):
                raise ValueError("slice step must be a multiple of the range step")

            slice_step = int(step // self.step)

        return slice(start_pos, stop_pos, slice_step)

    def _getitem_slice(self, key: slice) -> Self:

        key = self._normalize_slice(key)
        
        start_pos, stop_pos, slice_step = key.indices(self.length)

        if slice_step <= 0:
            raise ValueError("negative or zero slice steps are not supported yet")

        new_sr = self.sr.iloc[key].reset_index(drop=True)

        new_start = self.timedelta_at(start_pos)
        new_step = self.step * slice_step
        new_period = (self.timedelta_at(stop_pos) - self.step) // new_step

        return TimedeltaRangeSr(
            new_sr,
            metadata=(new_start, 
                      new_period, 
                      self.unit, 
                      new_step),
        )

    def to_series_with_timedelta_index(self) -> pd.Series:
        idx = np.array([ self.start + self.step * i for i in range(self.length) ])

        return pd.Series(self.sr.to_numpy(), index=idx, name=self.sr.name)

    def concat(self, objects: list[Self]) -> Self:

        if not objects:
            raise ValueError("cannot concat an empty list")

        all_objects = [self] + objects

        for a, b in zip(all_objects, objects):

            if a.stop != b.start:
                raise ValueError(
                    "cannot concat: ranges are not contiguous "
                    f"between {a.stop} and {b.start}"
                )

        new_sr = pd.concat(
            [obj.sr for obj in all_objects],
            ignore_index=True,
        )

        return TimedeltaRangeSr(
            new_sr,
            metadata=(self.start, 
                      np.array([cur_obj.length for cur_obj in all_objects]).sum(), 
                      self.unit, 
                      self.step),
        )

    def _lower_bound_pos(self, other: pd.Timedelta) -> int:
        if other <= self.start:
            return 0
    
        if other > self.stop:
            return self.length
    
        delta = other - self.start
        q = delta // self.step
        r = delta % self.step
    
        if r == pd.Timedelta(0):
            return int(q)
    
        return int(q) + 1
    
    
    def _upper_bound_pos(self, other: pd.Timedelta) -> int:
        if other < self.start:
            return 0
    
        if other >= self.stop:
            return self.length
    
        delta = other - self.start
        q = delta // self.step
        r = delta % self.step
    
        return int(q) + 1 
    
    def _compare_datetime(self, other, op: str):
        other = pd.Timedelta(other)
    
        values = np.zeros(self.length, dtype=bool)
    
        lb = self._lower_bound_pos(other)
        ub = self._upper_bound_pos(other)
    
        match op:
            case "<":
                values[:lb] = True
            case "<=":
                values[:ub] = True
            case ">":
                values[ub:] = True
            case ">=":
                values[lb:] = True
            case "==":
                values[lb:ub] = True
            case "!=":
                values[:] = True
                values[lb:ub] = False
            case _:
                raise ValueError(f"unknown comparison operator: {op}")
    
        return values

    def __lt__(self, other):
        return self._compare_datetime(other, "<")

    def __le__(self, other):
        return self._compare_datetime(other, "<=")
    
    def __eq__(self, other):
        return self._compare_datetime(other, "==")
    
    def __ne__(self, other):
        return self._compare_datetime(other, "!=")
    
    def __ge__(self, other):
        return self._compare_datetime(other, ">=")
    
    def __gt__(self, other):
        return self._compare_datetime(other, ">")

```

Basically, nothing too different from Custom `DatetimeRangeSr`.

Here is some use of it.

Convertions to a `pd.Series` with `pd.TimedeltaIndex`.

```python

ser = pd.Series([10, 20, 30, 22, 56])

trs = TimedeltaRangeSr(
    ser,
    metadata=(
        pd.Timedelta(0),
        5,
        "D",
        pd.Timedelta(days=2), 
    ),
)

print(trs.to_series_with_timedelta_index())

print(trs.to_series_with_timedelta_index().index)

```

Output.

```

0 days    10
2 days    20
4 days    30
6 days    22
8 days    56
dtype: int64

TimedeltaIndex(['0 days', '2 days', '4 days', '6 days', '8 days'], dtype='timedelta64[ns]', freq=None)

```

Random access.

```python

print(trs[pd.Timedelta(days=2)])

```

Output.

```python

20

```

Random access, slicing.

```python

print(trs[pd.Timedelta(days=2):pd.Timedelta(days=8):1])

```

Output.

```

TimedeltaRangeSr(start=Timedelta('2 days 00:00:00'), stop=Timedelta('8 days 00:00:00'), period=3, unit='D', step=Timedelta('2 days 00:00:00'), length=3)
0    20
1    30
2    22
dtype: int64

```

Comparisons operations.

```python

print(trs > pd.Timedelta(days=2))

```

Output.

```

[False False  True  True  True]

```

Concatenation

```python

ser2 = pd.Series([10, 20, 30, 22, 56] * 2)

trs2 = TimedeltaRangeSr(
    ser2,
    metadata=(
        trs.stop,
        "D",
        pd.Timedelta(days=2), 
    ),
)

print(trs.concat([trs2]))

```

Output.

```python

TimedeltaRangeSr(start=Timedelta('0 days 00:00:00'), stop=Timedelta('30 days 00:00:00'), period=15, unit='D', step=Timedelta('2 days 00:00:00'), length=15)
0     10
1     20
2     30
3     22
4     56
5     10
6     20
7     30
8     22
9     56
10    10
11    20
12    30
13    22
14    56
dtype: int64

```

### API discussion

Hmm, I would like to expose another constructor API that takes a `start`, `step` and `end` timedelta instead of `start` and `step`.

**In this API design, the question is now: Should it bedata-first.**

And imo, it should be, meaning that the `index`, which is metadata must fit the data, like we already have, but it would be nice to also implement other constructor variants.

We just have to dispatch.

```python

def __init__(
    self,
    sr: pd.Series,
    metadata,
): 
    match metadata:
        case (a, b, c):
            self.__init1(sr, metadata)
        case (a, b):
            self.__init2(sr, metadata)
        case _:
            raise ValueError("`metadata` must be a tupple of 2 - (start, stop) or 3 (start, stop, step)")

def __init1(
    self,
    sr: pd.Series,
    metadata: tuple[pd.Timestamp, pd.Timestamp, pd.Timedelta],
):
    start, stop, step = metadata

    if not isinstance(start, pd.Timestamp):
        start = pd.Timestamp(start)

    if not isinstance(stop, pd.Timestamp):
        stop = pd.Timestamp(stop)

    if not isinstance(step, pd.Timedelta):
        step = pd.Timedelta(step)

    if step <= pd.Timedelta(0):
        raise ValueError("step must be positive")

    if not start < stop:
        raise ValueError("stop must be higher than start")

    expected_len = (stop - start) // step

    if start + expected_len * step != stop:
        raise ValueError("stop must align exactly with start + n * step")

    if len(sr) != expected_len:
        raise ValueError(
            f"Series length does not match datetime range: "
            f"len(sr)={len(sr)}, expected={expected_len}"
        )

    self.sr = sr.reset_index(drop=True)
    self.start = start
    self.stop = stop
    self.step = step
    self.length = int(expected_len)

def __init2(
    self,
    sr: pd.Series,
    metadata: tuple[pd.Timestamp, pd.Timestamp],
):
    start, stop = metadata

    if not isinstance(start, pd.Timestamp):
        start = pd.Timestamp(start)

    if not isinstance(stop, pd.Timestamp):
        stop = pd.Timestamp(stop)
    
    if not start < stop:
        raise ValueError("stop must be higher than start")

    step = (stop - start) / len(sr)

    expected_len = (stop - start) // step

    if start + expected_len * step != stop:
        raise ValueError("stop must align exactly with start + n * step")

    if len(sr) != expected_len:
        raise ValueError(
            f"Series length does not match datetime range: "
            f"len(sr)={len(sr)}, expected={expected_len}"
        )

    self.sr = sr.reset_index(drop=True)
    self.start = start
    self.stop = stop
    self.step = step
    self.length = int(expected_len)

```

Now, it works.

```python

drs3 = DatetimeRangeSr(
    ser2,
    metadata=(
        pd.Timestamp("2024-01-06"),
        pd.Timestamp("2024-01-16"),
    ),
)

print(drs3)

```

Output:

```

DatetimeRangeSr(start=Timestamp('2024-01-06 00:00:00'), stop=Timestamp('2024-01-16 00:00:00'), step=Timedelta('1 days 00:00:00'), length=10)
0    10
1    20
2    30
3    22
4    56
5    10
6    20
7    30
8    22
9    56
dtype: int64

```

And yess, you are not dreaming, we can do pattern-matching on tupple (a bit Haskellish), example:

```python

match metadata:
    case (a, b, c):
        self.__init1(sr, metadata)
    case (a, b):
        self.__init2(sr, metadata)
    case _:
        raise ValueError("`metadata` must be a tupple of 2 - (start, stop) or 3 (start, stop, step)")

```

### Some convertions

At this point I should talsk about comon convertion you'll need.

From `pd.Timestamp` to `pd.Timedelta`.

```python

>>> pd.Timestamp("1970-01-01 00:00:00").timestamp()
0.0

>>> pd.Timedelta(pd.Timestamp("2024-01-01 00:00:12").timestamp(), unit="s")
Timedelta('19723 days 00:00:12')

```

`.timestamp()` converts to sec from 1st Jan 1970 and then pass it to `pd.Timedlta`.

Here, with another.

```python

>>> pd.Timedelta(pd.Timestamp("2024-01-01 00:00:12", tz="Europe/Paris").timestamp(), unit="s")
Timedelta('19722 days 23:00:12')

```

Adding a `pd.Timedelta` and a `pd.Timestamp` obviously returns a `pd.Timestamp` (not like substracting 2 `pd.Timestamp` that also obviously return a `pd.Timedelta`):

```python

>>> pd.Timedelta(days=1) + pd.Timestamp("2024-01-01")
Timestamp('2024-01-02 00:00:00')

```

But in fact internally it does.

```python

>>> pd.Timestamp((pd.Timedelta(days=1).total_seconds() + pd.Timestamp("2024-01-01").timestamp()) * 10**9)
Timestamp('2024-01-02 00:00:00')

```

But we can get rid of the `10**9`, because both objects store nanoseconds as `.value`.

```python

>>> pd.Timestamp(pd.Timedelta(days=1).value + pd.Timestamp("2024-01-01").value)
Timestamp('2024-01-02 00:00:00')

```

So now we can construct object with recursive synthax lol:

```python

>>> pd.Timedelta(nanoseconds=pd.Timedelta(nanoseconds=4).value)
Timedelta('0 days 00:00:00.000000004')

```

### Custom `PeriodRangeIndex`

Basically, adapt the same mental model for `pd.Period`.

### `pd.IntervalIndex`

Here you index values by an interval.

See it like a fancy `pd.CategoricalIndex`.

```python

>>> x = pd.Series(
        [1, 2, 3, 4], 
        index=pd.IntervalIndex.from_arrays([0, 2, 3.5, 4.6], 
                                           [1, 3, 4, 6], 
                                           closed="both"))

>>> x
[0.0, 1.0]    1
[2.0, 3.0]    2
[3.5, 4.0]    3
[4.6, 6.0]    4
dtype: int64

```

It literaly means that you can reason like: What is the value that is associated to the interval where `X` is in ?

```python

>>> x[3]
np.int64(2)

```

Because `3` belongs to `[2.0, 3.0]`.

And yess even if `3` is the upper bound.

Because of the `closed="both"` that stipulates that both bounds must be inclusive.

Here are the possible values:

```

both
neither
left
right

```

Going back to the semantics of the interval index, you can also get the position of the interval that contains a certain value.

```python

>>> x.index.get_loc(2.5)
np.int64(1)

```

If I have multiple matches like in tis case, it will return a slice:

```python

>>> x = pd.IntervalIndex.from_arrays([0, 1, 2], [1, 2.5, 3], closed = "both")

>>> x
IntervalIndex([[0.0, 1.0], [1.0, 2.5], [2.0, 3.0]], dtype='interval[float64, both]')

>>> x.get_loc(2.3)
slice(1, 3, None)

```

Or as a boolean vector.

```python

>>> x.index.contains(2.5)
array([False,  True, False, False])

```

Of course, an interval where upper and lower bound is the same but both inclusive still contains one point.

```python

>>> pd.IntervalIndex.from_breaks([1, 1], closed="both").contains(1)
array([ True])

```

But only for `closed="both`:

```python

>>> pd.IntervalIndex.from_breaks([1, 1], closed="left").contains(1)
array([False])

```

`pd.IntervalIndex` exposes left (lower) bounds and right (upper) bounds.

```python

>>> x.index.left
Index([0.0, 2.0, 3.5, 4.6], dtype='float64')

>>> x.index.right
Index([1.0, 3.0, 4.0, 6.0], dtype='float64')

```

That's fun, they are `pd.Index`.

I wander if they would be `pd.RangeIndex` if the step wuld be constant.

```python

>>> idx = pd.IntervalIndex.from_breaks([1, 2, 3, 4, 5, 6], closed="both")

>>> idx
IntervalIndex([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]], dtype='interval[int64, both]')

>>> idx.left
Index([1, 2, 3, 4, 5], dtype='int64')

>>> idx.right
Index([2, 3, 4, 5, 6], dtype='int64')

```

Unfortunately, it's not smart enougt to detect that it can be a `pd.RangeIndex`.

How, I did not speak yet about the other constructors.

Basically, you can construct via the classic `pd.interval_range()`.

```python3

>>> pd.interval_range(start=0, end=12, freq=2, closed="both")
IntervalIndex([[0, 2], [2, 4], [4, 6], [6, 8], [8, 10], [10, 12]], dtype='interval[int64, both]')

```

And seriously, this is the constructor where they could have optimize storage for the uper and lower bounds because `freq` is constant, but they did not do it...

```python

>>> pd.interval_range(start=0, end=12, freq=2, closed="both").left
Index([0, 2, 4, 6, 8, 10], dtype='int64')

>>> pd.interval_range(start=0, end=12, freq=2, closed="both").right
Index([2, 4, 6, 8, 10, 12], dtype='int64')

```

The `.from_arrays()` constructor is permissive, all iterable containers that respect the dimensons are accepted, you can mix them together for the bounds.

```python

>>> pd.IntervalIndex.from_arrays(left=[1, 3, 5], right=[2, 4, 6], closed="both")
IntervalIndex([[1, 2], [3, 4], [5, 6]], dtype='interval[int64, both]')

>>> pd.IntervalIndex.from_arrays(left=[1, 3, 5], right={2, 4, 6}, closed="both")
IntervalIndex([[1, 2], [3, 4], [5, 6]], dtype='interval[int64, both]')

>>> pd.IntervalIndex.from_arrays(left={1, 3, 5}, right={2, 4, 6}, closed="both")
IntervalIndex([[1, 2], [3, 4], [5, 6]], dtype='interval[int64, both]')

>>> pd.IntervalIndex.from_arrays(left=(1, 3, 5), right=(2, 4, 6), closed="both")
IntervalIndex([[1, 2], [3, 4], [5, 6]], dtype='interval[int64, both]')

```

When you knwo that your intervals are contiguous, you can use `.from_breaks()` method.

For example:

```python

>>> pd.IntervalIndex.from_breaks((2, 4, 6), closed="both")
IntervalIndex([[2, 4], [4, 6]], dtype='interval[int64, both]')

```

`pd.IntevalIndex` supports overlapping intervals.

```python

>>> pd.IntervalIndex.from_breaks([1, 1, 1, 1], closed="left")
IntervalIndex([[1, 1), [1, 1), [1, 1)], dtype='interval[int64, left]')

```

`.contains()` works properly.

```python

>>> pd.IntervalIndex.from_breaks([1, 1, 1, 1], closed="both").contains(1)
array([ True,  True,  True])

```

And as written before, `.get_loc()` returns a slice instead of a scalar.

```python

>>> pd.IntervalIndex.from_breaks([1, 1, 1, 1], closed="both").get_loc(1)
slice(0, 3, None)

```

It's now time to speak about its special methods.

First test if the interval are overlaping.

```python

>>> idx = pd.IntervalIndex.from_breaks([1, 1, 1, 1], closed="both")
>>> idx.is_overlapping
True

```

And the other one is for testing if the interval are not overlapping and strictly increasing.

```python

>>> idx.is_non_overlapping_monotonic
False

```

Because they're overlapping.

Now, I want to test intervals that are not overlapping (disjoints) but not ordered increasingly.

You note that for creating this kind of interval `index`, we can't use `pd.IntervalIndex.from_breaks()`, because in this design all values must be sorted, because of course lower bound of an interval must be lower than its upper bound (that i why the following error is telling us):

```python

>>> pd.IntervalIndex.from_breaks([1, 2, -1, 0])

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/interval.py", line 324, in from_breaks
    array = IntervalArray.from_breaks(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/interval.py", line 528, in from_breaks
    return cls.from_arrays(breaks[:-1], breaks[1:], closed, copy=copy, dtype=dtype)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/interval.py", line 650, in from_arrays
    cls._validate(left, right, dtype=dtype)
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/interval.py", line 782, in _validate
    raise ValueError(msg)
ValueError: left side of interval must be <= right side

```

So we must use the `pd.IntervalIndex.from_arrays()` API.

```python

>>> pd.IntervalIndex.from_arrays(
        left={1, 0}, 
        right={2, 1}, 
        closed="both"
    ).is_non_overlapping_monotonic

False

```

--> Expected

So an interval index that returns `True` for this value is an interval index that we **can** create with `.from_breaks()` method or this one.

```python

>>> pd.IntervalIndex.from_arrays(left={0, 1}, right={1, 2}, closed="both").is_non_overlapping_monotonic
False

```

Wait what ?

Haa yess, it is because of `closed="both"`. 

With all 3 others its possible valuesit obviously returns `True`:

```python

>>> pd.IntervalIndex.from_arrays(left={0, 1}, right={1, 2}, closed="neither").is_non_overlapping_monotonic
True

>>> pd.IntervalIndex.from_arrays(left={0, 1}, right={1, 2}, closed="right").is_non_overlapping_monotonic
True

>>> pd.IntervalIndex.from_arrays(left={0, 1}, right={1, 2}, closed="left").is_non_overlapping_monotonic
True

```

There is something related to `pd.IntervalIndex`.

```python

>>> pd.cut(pd.Series([7, 8, 17, 21, 55]), bins=[0, 10, 20, 30])

0     (0.0, 10.0]
1     (0.0, 10.0]
2    (10.0, 20.0]
3    (20.0, 30.0]
4             NaN
dtype: category
Categories (3, interval[int64, right]): [(0, 10] < (10, 20] < (20, 30]]

```

Yess, this returned a `pd.Series`.

```python

>>> type(pd.cut(pd.Series([7, 8, 17, 21, 55]), bins=[0, 10, 20, 30]))
<class 'pandas.Series'>

```

And the index is a normal `pd.RangeIndex`.

```python

>>> pd.cut(pd.Series([7, 8, 17, 21, 55]), bins=[0, 10, 20, 30]).index
RangeIndex(start=0, stop=5, step=1)

```

But, what are the values ?

```python

>>> pd.cut(pd.Series([7, 8, 17, 21, 55]), bins=[0, 10, 20, 30]).values

[(0.0, 10.0], (0.0, 10.0], (10.0, 20.0], (20.0, 30.0], NaN]
Categories (3, interval[int64, right]): [(0, 10] < (10, 20] < (20, 30]]

>>> type(pd.cut(pd.Series([7, 8, 17, 21, 55]), bins=[0, 10, 20, 30]).values)
<class 'pandas.Categorical'>

```

They are `pd.Categorical`, (we have already talked about this one in the [pd.CategoricalIndex](#`pd.CategoricalIndex`) part).

Then when I do:

```python

>>> cats = pd.cut(pd.Series([7, 8, 17, 21, 55]), bins=[0, 10, 20, 30])

>>> cats[1]
Interval(0, 10, closed='right')

```

Internally, it roughly does:

```python

>>> cats.cat.categories[cats.cat.codes[1]]
Interval(0, 10, closed='right')

```

Or this:

```python

>>> x3b.values.categories[x3b.values.codes[1]]
Interval(0, 10, closed='right')

>>> # OR in newer attribute

>>> x3b.values.categories[x3b.array.codes[1]]
Interval(0, 10, closed='right')

```

With one important nuance as you see, missing values have codes `-1`, so it does not strictly respect the expression above.

```python

>>> cats.cat.codes
0    0
1    0
2    1
3    2
4   -1
dtype: int8

```

And, damn, even `codes` is a `pd.Series`, i hope its index is a `pd.RangeIndex`.

```python

>>> cats.cat.codes.index
RangeIndex(start=0, stop=5, step=1)

```

We are saved !

By the way, technically it would be simple to directly return a `pd.Categorical` instead of wrapping it to a `pd.Series`.

This is just to preserve the shape of the input, but we have this behavior when we pass `np.array()` or directly a list into `pd.cut()`:

```python

>>> x3a = pd.cut([7, 8, 17, 21, 55], bins = [0, 10, 20, 30])

>>> x3c = pd.cut(np.array([7, 8, 17, 21, 55]), bins = [0, 10, 20, 30])

>>> x3a
[(0.0, 10.0], (0.0, 10.0], (10.0, 20.0], (20.0, 30.0], NaN]
Categories (3, interval[int64, right]): [(0, 10] < (10, 20] < (20, 30]]

>>> x3c
[(0.0, 10.0], (0.0, 10.0], (10.0, 20.0], (20.0, 30.0], NaN]
Categories (3, interval[int64, right]): [(0, 10] < (10, 20] < (20, 30]]

>>> x3c.codes
array([ 0,  0,  1,  2, -1], dtype=int8)

>>> x3a.codes
array([ 0,  0,  1,  2, -1], dtype=int8)

>>> x3a.categories
IntervalIndex([(0, 10], (10, 20], (20, 30]], dtype='interval[int64, right]')

>>> x3c.categories
IntervalIndex([(0, 10], (10, 20], (20, 30]], dtype='interval[int64, right]')

```

Therefore, they have a much lower size:

```python

>>> [sys.getsizeof(a) for a in (x3a, x3b, x3c)]
[85, 217, 85]

```

So be carefull !

Also, note that `NaN` values are in fact `np.nan`, and those, when compared, always return `False`, this is why:

```python

>>> x3a == x3c
array([ True,  True,  True,  True, False])

```

Because:

```python

>>> np.nan == np.nan
False

```

Here, the `pd.Categorical` contains `pd.Interval`.

Btw, we can construct one as the following:

```python

>>> pd.Interval(1, 2, closed = "neither")
Interval(1, 2, closed='neither')

```

But, it is a more geenral container that can contain other values type:

```python

pd.Categorical(["small", "medium", "large"])
# scalar values are strings

pd.Categorical([1, 2, 1])
# scalar values are integers

pd.cut([7, 8, 17], bins=[0, 10, 20])
# scalar values are pd.Interval

```

Therefore, we can use a `pd.Categorical` to create the appropriate `Index`.

It is very permissive as you see:

```python

>>> x3a

[(0.0, 10.0], (0.0, 10.0], (10.0, 20.0], (20.0, 30.0], NaN]
Categories (3, interval[int64, right]): [(0, 10] < (10, 20] < (20, 30]]

>>> pd.CategoricalIndex(x3a)

CategoricalIndex([(0.0, 10.0], (0.0, 10.0], (10.0, 20.0], (20.0, 30.0], nan], categories=[(0, 10], (10, 20], (20, 30]], ordered=True, dtype='category')

>>> pd.IntervalIndex(x3a)

IntervalIndex([(0.0, 10.0], (0.0, 10.0], (10.0, 20.0], (20.0, 30.0], nan], dtype='interval[float64, right]')

```

So, now we can answer the following question:

"In which interval does my value fall ?"

```python

>>> ser
0     2
1     7
2    21
3    19
4    13
5    27
dtype: int64

>>> pd.cut(ser, bins=[0, 10, 20, 30])[np.where(ser.values == 21)[0][0]]
Interval(0, 10, closed='right')

# OR

>>> pd.cut(ser, bins = [0, 10, 20, 30])[np.where(ser == 2)[0][0]]
Interval(0, 10, closed='right')

```

Just a small point on `np.where()`.

First a `np.array` shape / dimension must be symetric, for example:

```python

[[1, 2], 3]

```

Can be drawn as.

```python

    /\
   /  \
  /\   3
 1  2

```

A `np.array` is the same.

**Hmm, but not totally, the tree must be symetric.**

So this is invalid.

```python

>>> np.array([[1, 2], 3])

```

Neither this.

```python

>>> np.array([[1, 2], [3]])

```

But this is.

```python

>>> np.array([[1, 2], [3, 4]])
array([[1, 2],
       [3, 4]])

```

Or just this.

```python

>>> np.array([1, 2, 3, 4])
array([1, 2, 3, 4])

```

And this is not.

```python

>>> np.array([[1, 2, [3, 4]], [5, 6, [7, 8]]])

```

And this.

```python

>>> np.array([[[1, 2], 3, 4], [5, 6, [7, 8]]])

```

- "But, wait the last one is symetric !"

Yess, but I forgot to tell you the other rule, they must also share the same depth level.

So this is not symetric but this one is.

```python

>>> np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

array([[[1, 2],
        [3, 4]],

       [[5, 6],
        [7, 8]]])

```

Now, going back to `np.where()`, because this is the equivalent of `.index()` for list but for searchin scalar value(s), multiple index must be outpted, each one corresponding to a depth level.

For example.

```python

>>> np.where(np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]) == 6)

(array([1]), array([0]), array([1]))

```

Because `6` is at the second list, then in the first list and finally at the second index of this last list.

The neat thing with `np.where()` is that you can search for multiple scalars in one call.

```python

>>> np.where(np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]) == [5, 8])

(array([1, 1]), array([0, 1]), array([0, 1]))

```

Its why the output is a tupple of `array`.

- 5 -> 1, 0, 0

- 8 -> 1, 1, 1

If it is not found, then it will just not take it into account for the returned data structure:

```python

>>> np.where(np.array([[[1, 2], [3, 4]], [[5, 6], [7, 5]]]) == [5, 8])

(array([1]), array([0]), array([0]))

```

And it acts like a match of the first sequence, so if you want to match the indices of the value that you know appears 2 times or so, do the following:

```python

>>> np.where(np.array([[[1, 2], [3, 4]], [[5, 6], [7, 5]]]) == [5, 5])

(array([1, 1]), array([0, 1]), array([0, 1]))

```

You get the position of its first and second occurence.

It works the same with tuple synthax.

```python

>>> np.where(arr == (5, 8))

(array([1, 1]), array([0, 1]), array([0, 1]))

```

But not with arr (`{...}`) synthax, because `set` does not maintain the order of their elements (so the visual order we see is not assured to be the same in the internal representation).

```python

>>> np.where(arr == {5, 8})

(array([], dtype=int64), array([], dtype=int64), array([], dtype=int64))

```

It thinks that the whole `{5, 8}` is the value (`set`) we are searching for, so this work:

```python

>>> np.where(np.array([{1, 2}, {3, 4}]) == {3, 4})
(array([1]),)

>>> np.where(np.array([{1, 2}, {3, 4}]) == {4, 3})
(array([1]),)

>>> np.where(np.array([{1, 2}, {3, 4}]) == {4, 3, 3})
(array([1]),)

```

And, did you know that numpy array supports tuple random acess ?

I mean look those are equivalent.

```python

>>> arr[1][0][1]
np.int64(6)

```

And.

```python

>>> arr[(1, 0, 1)]
np.int64(6)

```

Or even:

```python

>>> arr[( np.array([1, 0]), np.array([0, 1]), np.array([1, 1]) )]
array([6, 4])

```

Then we can do:

```python

>>> f = lambda a, tpl: a[tpl]

>>> f(arr, np.where(arr==[5, 8]))
array([5, 8])

```

Then it just selects elements that exists **without returning an error when it did not find it**.

```python

>>> f(arr, np.where(arr == 22))
array([], dtype=int64)

>>> arr
array([[[1, 2],
        [3, 4]],

       [[5, 6],
        [7, 8]]])

>>> f(arr, np.where(arr==[5, 18]))
array([5])
```

Now, the beauty of `pd.IntervalIndex` is to retrieve values based on their bins !

```python

>>> x = pd.Series(["small", "medium", "large", "xxl"], index=pd.IntervalIndex.from_breaks([1, 2, 3, 4, 5]))

>>> x
(1, 2]     small
(2, 3]    medium
(3, 4]     large
(4, 5]       xxl
dtype: str

>>> x[1.2]
'small'

```

This is why I talked earlier about fancy `pd.CategoricalIndex`, it's like questioning to what categories this value belongs to.

Here is an example.

What we can do now is to assign category to `pd.Series` elements.

```python

>>> x = pd.Series(["small", "medium", "large", "xxl"], 
                  index=pd.IntervalIndex.from_breaks([1, 2, 3, 4, 5], 
                  closed="both"))

>>> x2 = pd.Series(np.random.normal(1, 2.5, 12).clip(1, 5))

>>> x2
0     4.396643
1     2.795797
2     1.000000
3     3.856331
4     2.477599
5     1.000000
6     1.000000
7     1.609508
8     1.000000
9     1.000000
10    5.000000
11    3.881804
dtype: float64

```

I cliped `.clip(min, max)` values to lower and upper bounds of the interval index of `x` (which are inclusive).

`.clip()` wont delete values that are out of bounds, but round them to the nearest bound value:

```python

>>> np.array([1, 2, 3, 4, 5, 6]).clip(0, 5)
array([1, 2, 3, 4, 5, 5])

```

Now, I just categorize them mapping a function to retrive category based on values.

```python

>>> x2.map(lambda v: x[v])
0        xxl
1     medium
2      small
3      large
4     medium
5      small
6      small
7      small
8      small
9      small
10       xxl
11     large
dtype: str

```

It also works with `pd.Timestamp`.

```python

>>> x = pd.Series(["small", "medium", "large", "xxl"], 
                  index=pd.IntervalIndex.from_breaks([
                                                        pd.Timestamp("2024-01-01"), 
                                                        pd.Timestamp("2024-01-02"), 
                                                        pd.Timestamp("2024-01-03"), 
                                                        pd.Timestamp("2024-01-04"), 
                                                        pd.Timestamp("2024-01-05")
                                                     ], 
                                                     closed="both"))

>>> x
[2024-01-01 00:00:00, 2024-01-02 00:00:00]     small
[2024-01-02 00:00:00, 2024-01-03 00:00:00]    medium
[2024-01-03 00:00:00, 2024-01-04 00:00:00]     large
[2024-01-04 00:00:00, 2024-01-05 00:00:00]       xxl
dtype: str

```

Then we create the data to labelize / categorize.

```python

>>> x2 = pd.Series(np.random.normal(1, 2.5, 12).clip(1, 5).round())

>>> x2 = x2.map(lambda x: pd.Timestamp(f"2024-01-0{int(x)}"))

>>> x2
0    2024-01-03
1    2024-01-01
2    2024-01-01
3    2024-01-05
4    2024-01-02
5    2024-01-01
6    2024-01-01
7    2024-01-01
8    2024-01-02
9    2024-01-01
10   2024-01-01
11   2024-01-01
dtype: datetime64[us]

```

And then we categorize.

```python

>>> x2.map(lambda vl: x[vl])

0     [2024-01-02 00:00:00, 2024-01-03 00:00:00]    ...
1                                                 small
2                                                 small
3                                                   xxl
4     [2024-01-01 00:00:00, 2024-01-02 00:00:00]    ...
5                                                 small
6                                                 small
7                                                 small
8     [2024-01-01 00:00:00, 2024-01-02 00:00:00]    ...
9                                                 small
10                                                small
11                                                small
dtype: object

```

wait, wait, wait, WTf is that ?

I mean yeah that's a `pd.Series`, but have you seen its values ?

```python

>>> x2.map(lambda vl: x[vl]).values
array([[2024-01-02 00:00:00, 2024-01-03 00:00:00]    medium
       [2024-01-03 00:00:00, 2024-01-04 00:00:00]     large
       dtype: str                                          , 'small',
       'small', 'xxl',
       [2024-01-01 00:00:00, 2024-01-02 00:00:00]     small
       [2024-01-02 00:00:00, 2024-01-03 00:00:00]    medium
       dtype: str                                          , 'small',
       'small', 'small',
       [2024-01-01 00:00:00, 2024-01-02 00:00:00]     small
       [2024-01-02 00:00:00, 2024-01-03 00:00:00]    medium
       dtype: str                                          , 'small',
       'small', 'small'], dtype=object)

```

And array of -- oh my gosh, would it be `pd.Series` and `string` ?

```python

>>> x2.map(lambda vl: x[vl]).values[0]
[2024-01-02 00:00:00, 2024-01-03 00:00:00]    medium
[2024-01-03 00:00:00, 2024-01-04 00:00:00]     large
dtype: str

>>> type(x2.map(lambda vl: x[vl]).values[0])
<class 'pandas.Series'>

>>> x2.map(lambda vl: x[vl]).values[0].index
IntervalIndex([[2024-01-02 00:00:00, 2024-01-03 00:00:00], [2024-01-03 00:00:00, 2024-01-04 00:00:00]], dtype='interval[datetime64[us], both]')

>>> x2.map(lambda vl: x[vl]).values[-1]
'small'

```

**Yess, they are !!!**

Why ?

Because remember `closed="both"` (all 2 bounds are inclusive, the opposite of `"neither"`).

And look at those `x2` values.

```python

>>> x2
0    2024-01-03
1    2024-01-01
2    2024-01-01
3    2024-01-05
4    2024-01-02
5    2024-01-01
6    2024-01-01
7    2024-01-01
8    2024-01-02
9    2024-01-01
10   2024-01-01
11   2024-01-01
dtype: datetime64[us]

```

They are for a good part, on upper and lower bounds of 2 intervals -> 2 categories.

Apart from the first one for example (all the `"2024-01-01"` -> just one lower bound -> one string object).

```python

>>> x2.map(lambda vl: x[vl]).values[1]
'small'

```

To have a type uniform `.values`, we can make only one interval bound inclusive:

```python

import pandas as pd
import numpy as np

idx = pd.IntervalIndex.from_breaks(
    pd.date_range("2024-01-01", periods=6, freq="D"),
    closed="left"
)

x = pd.Series(["small", "medium", "large", "xl", "xxl"], index=idx)

x_origin = pd.Series(
    np.random.normal(1, 2.5, 12).clip(1, 5).round()
)

x2 = x_origin.map(lambda v: pd.Timestamp(f"2024-01-{int(v):02d}"))

x3 = x2.map(lambda vl: x[vl])

print(x3)

```

Result:

```

❯ python3 test_ser.py
0         xl
1      small
2      small
3      small
4      small
5      small
6      small
7     medium
8      small
9      small
10     small
11     small
dtype: str

```

Here, this is super dangerous to create the `pd.IntervalIndex` with `closed = "neither"` because then the search will fail (because all at bounds), and when it failsit **does not return a np.nan**, but **raises an error**:

```python

Traceback (most recent call last):
  File "/home/juju/gitrepos/julienlargetpiet.tech/plot/test_ser.py", line 17, in <module>
    x3 = x2.map(lambda vl: x[vl])
         ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/series.py", line 4675, in map
    new_values = self._map_values(func, na_action=na_action)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/base.py", line 1020, in _map_values
    return arr.map(mapper, na_action=na_action)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/_mixins.py", line 83, in method
    return meth(self, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/arrays/datetimelike.py", line 767, in map
    result = map_array(self, mapper, na_action=na_action)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/algorithms.py", line 1710, in map_array
    return lib.map_infer(values, mapper)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "pandas/_libs/lib.pyx", line 3071, in pandas._libs.lib.map_infer
  File "/home/juju/gitrepos/julienlargetpiet.tech/plot/test_ser.py", line 17, in <lambda>
    x3 = x2.map(lambda vl: x[vl])
                           ~^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/series.py", line 959, in __getitem__
    return self._get_value(key)
           ^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/series.py", line 1046, in _get_value
    loc = self.index.get_loc(label)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/indexes/interval.py", line 814, in get_loc
    raise KeyError(key)
KeyError: Timestamp('2024-01-01 00:00:00')

```

Also, how does a numpy array can hold different type at the same time, like a string and a `pd.Series` ???"

First intuition, they are both objects so it is like having:

```python

>>> np.array([1, {1, 2, 3}])

array([1, {1, 2, 3}], dtype=object)

```

Because if I try to reproduce the shape:

```python
>>> np.array(["small", pd.Series([1, 2])])

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (2,) + inhomogeneous part.
```

Yup, an error.

Then, what ?

In fact there is this "tiny" option that you can set while constructing an array --> `dtype`.

Normally it is set to `None`, meaning `numpy` inferes the type from the data.

But sometimes it needs help, so set it to `"object"`

```python

>>> np.array(["small", pd.Series([1, 2])], dtype = "object")
array(['small', 0    1
                1    2
                dtype: int64], dtype=object)

```

When infering, it also detects if the shape of all the objects are the same, and here this isn't the case.

This is why it did not work.

We have the same concept with other containers of course:

```python

>>> np.array([1, [1]], dtype=None)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (2,) + inhomogeneous part.

>>> np.array([1, (1,)], dtype=None)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (2,) + inhomogeneous part.

```

Note, the following works:

```python

>>> np.array([1, (1)], dtype=None)
array([1, 1])

```

Because `(1)` is not a tuple but just an expression representing an integer in this case -> `(1,)` is a tuple.

Btw, in raw Python lists, it absolutely work because list can store variables from different types (no concept of `dtype` then no infering).


```python

>>> [1, pd.Series([1, 2]) ]

[1, 0    1
1    2
dtype: int64]

```

Also, a quick note on strings stored in `numpy.ndarray`.

For performance concerns it converts the strings to a `numpy._str` which is not exactly a `str`, but a mix of it and an array (fixed size).

Example:


```python

>>> np.array(["a-z", "sdsd"])
array(['a-z', 'sdsd'], dtype='<U4')

```

NumPy inferred the dtype `<U4`.

This does not mean the array has length 4. It means each element is stored as a fixed-width Unicode string that can hold up to 4 characters, because `"sdsd"` is the longest string passed to the constructor.

So every element has the same storage size. 

This gives `numpy` a predictable, contiguous memory layout, which is very different from a normal Python list of `str` objects.

But when you access a single element, `numpy` wraps it into a string-like scalar.

For example:

```python

>>> "a-b".split("-")
['a', 'b']

>>> np.array(["a-z", "sdsd"])[0].split("-")
['a', 'z']

```

The element returned by indexing is usually a `numpy.str_`, which behaves very much like a Python `str`:

```python

>>> type(np.array(["a-z", "sdsd"])[0])
<class 'numpy.str_'>

>>> isinstance(np.array(["a-z", "sdsd"])[0], str)
True

```

So the array storage is fixed-width, but the scalar you get back still supports normal string methods such as `.split()` or string operator overloading such as `+`:

```python

>>> np.array(["12DF", "dfdf"])[0] + "dfdfd"
'12DFdfdfd'

```

Also this storage `<UN` has consequences.

```python

>>> a = np.array(["a-z", "sdsd"])

>>> a[0] = "hello"

>>> a

array(['hell', 'sdsd'], dtype='<U4')

```

Because `dtype` is fixed at `<U4`, longer strings are truncated when assigned.

Here is another example of labelizing with `pd.Timedelta`:

```python

>>> idx = pd.IntervalIndex.from_breaks(
        [pd.Timedelta(days=1), pd.Timedelta(days=2), pd.Timedelta(days=3), 
        pd.Timedelta(days=4)], 
        closed="both"
)

>>> ser = pd.Series(["early", "mid", "late"], index=idx)

>>> ser

[1 days 00:00:00, 2 days 00:00:00]    early
[2 days 00:00:00, 3 days 00:00:00]      mid
[3 days 00:00:00, 4 days 00:00:00]     late
dtype: str

```

And now creating data to labelize.

```python

>>> ser2 = pd.Series(np.random.uniform(1, 4, 12)).map(lambda vl: pd.Timedelta(days=vl))

>>> ser2
0    2 days 21:38:43.802402493
1    3 days 08:43:10.202247026
2    2 days 22:44:02.396862022
3    1 days 12:25:00.984635749
4    3 days 18:59:06.272587609
5    1 days 19:28:46.593006243
6    2 days 19:46:45.232864534
7    3 days 06:32:40.820480225
8    2 days 09:15:57.313691881
9    1 days 13:43:25.461874851
10   1 days 06:05:25.508552033
11   3 days 18:08:41.716050245
dtype: timedelta64[ns]

```

Finally labelizing.

```python

>>> ser2.map(lambda vl: ser[vl])

0       mid
1      late
2       mid
3     early
4      late
5     early
6       mid
7      late
8       mid
9     early
10    early
11     late
dtype: str

```

## Would you mind take some DataFrame ?

You can create a `pd.DataFrame` in multiple ways.

### First, by reading a `CSV`.

```python

df = pd.read_csv("example.csv",
                 sep=",",
                 encoding="latin1")

```

For a better control of columns types, which led to a **faster ingestion process** (because no column type inference), you can choos column types directly.

But dates are something special, you can't tell that a column is a `datetime[us]` type directly in parsing.

For this example consider the following file.

```

name,age,city,price,date1
"Alice",25,"Paris",34.45,2024-01-15
"Bob",30,"New York, \"USA\"",55.3,2025-02-14

```

```python

df = pd.read_csv("file3.csv", 
                 dtype={"name": "string", 
                        "age": "int8", 
                        "city": "string", 
                        "price": "float32"})
print(df)
print(df.dtypes)

```

Output.

```

    name  age               city    price       date1
0  Alice   25              Paris  34.4375  2024-01-15
1    Bob   30  New York, \USA\""  55.3125  2025-02-14
name      string
age         int8
city      string
price    float16
date1        str # wrong
dtype: object

```

We need to specify columns that are dates, but wait ins't that what `dtype` stand for (assigning a type to a column) ?

Yess, but they introduced a specific option for that called `parse_dates`.

```

df = pd.read_csv("file3.csv", 
                 dtype={"name": "string", 
                        "age": "int8", 
                        "city": "string", 
                        "price": "float32"}, 
                 parse_dates=["date1"])
print(df)
print(df.dtypes)

```

Output.

```

    name  age               city      price      date1
0  Alice   25              Paris  34.450001 2024-01-15
1    Bob   30  New York, \USA\""  55.299999 2025-02-14
name             string
age                int8
city             string
price           float32
date1    datetime64[us] # finally
dtype: object

```

But if you do not trust the engine to actually parse you date.

You can just read it as:

```python

df = pd.read_csv("file3.csv", 
                 dtype={"name": "string", 
                        "age": "int8", 
                        "city": "string", 
                        "price": "float32"})

```

(Heare `date1` is `str`)

And after add your specific parsing logic inside the `pd.to_datetime()` function.

```python

df["date1"] = pd.to_datetime(df["date1"], format="%Y-%m-%d")
print(df.dtypes)

```

Output.

```

name             string
age                int8
city             string
price           float32
date1    datetime64[us]
dtype: object

```

#### More on Dates

Consider this file:

```

name,age,city,price,date1,date2
"Alice",25,"Paris",34.45,2024-01-15,02:01:55
"Bob",30,"New York, \"USA\"",55.3,2025-02-14,15:18:55

```

So, as we saw, we do:

```python

df = pd.read_csv("file3.csv", 
                 dtype={"name": "string", 
                        "age": "int8", 
                        "city": "string", 
                        "price": "float32"})

df["date1"] = pd.to_datetime(df["date1"], format="%Y-%m-%d")
df["date2"] = pd.to_datetime(df["date2"], format="%H:%M:%S")

print(df.dtypes)

```

Output.

```

name             string
age                int8
city             string
price           float32
date1    datetime64[us]
date2    datetime64[us]

```

So far so good, but look at the `date2` col.

```python

print(df)

```

Output.

```

    name  age               city      price      date1               date2
0  Alice   25              Paris  34.450001 2024-01-15 1900-01-01 02:01:55
1    Bob   30  New York, \USA\""  55.299999 2025-02-14 1900-01-01 15:18:55

```

Why `1900-01-01` added ?

That's a placeholder for pandas to store a full `datetime64[us]`.

Note that `date1` column also store `H`, `M` and `S`, yo just do not see it on display.

So if yo want to store just its time unit, store them as `datetime.time` object.

```python

df["date2"] = pd.to_datetime(df["date2"], format="%H:%M:%S").dt.time
print(df.dtypes)

print("###")

print(type(df["date2"].iloc[0]))

```

Output.

```

name             string
age                int8
city             string
price           float32
date1    datetime64[us]
date2            object
dtype: object

###

<class 'datetime.time'>

```

Comparisons

```

print(df["date1"][0] > df["date1"][1])

print(df["date2"][0] > df["date2"][1])

```

Output.

```

False
False

```

BUTTT !

They are heavier than `datetime64[us]` types.

```python3

print(df.memory_usage(deep=True))

```

Output

```

Index    132
name      24
age        2
city      38
price      8
date1     16
date2     96
dtype: int64

```

`datetime64[us]` as its name suggest is encoded with only 64 bits, so 2 rows times 8 bytes, we find the `16` bytes.

While `datetime.time` is an object, so we hve 1 pointer for each row -> 2 * 8 bytes = 16 bytes and because we have set `deep=True` in the `.memory_usage`, then it also counts the size of the `datetime.time` objects that are `40` bytes each:

```python

>>> sys.getsizeof(datetime.time(1))
40

```

So we have 16 + 2 * 40 = `96` bytes.

But isn't that strange ?

I mean look at:

```python

df["date1"] = pd.to_datetime(df["date1"], format="%Y-%m-%d")

```

and:

```python

df["date2"] = pd.to_datetime(df["date2"], format="%H:%M:%S").dt.time

```

It looks like objects from `"date1"` **should also contain `.dt.time`**, therefore `"date1"` column size should be much larger ?

But, in fact attribute access does not always mean "read a stored field".

When we write:

```python

obj.attr

```

Python may either:

1. read a real stored attribute from the object

2. call some logic that computes the value dynamically

In a class, it's usualy implemented with the `@property` flag:

```python

class Person:
    def __init__(self, birth_year):
        self.birth_year = birth_year

    @property
    def age(self):
        return 2026 - self.birth_year

```

And we use it like:

```python

p = Person(2000)

p.birth_year
# stored attribute

p.age
# computed on demand

```

`age` looks like an attribute, but behind the scenes it calls a method.

For our case, `.dt` is similar.

So this:

```python

df["date1"]

```

does not store `datetime.time` objects.

It stores compact integer timestamps.

But this:

```python

df["date1"].dt.time

```

creates a new object-dtype result.

#### Partial reads (Rows)

Yess you can read from a start row to an ending row.

Consder this file:

```

name,age,city,price,date1,date2
"Alice",25,"Paris",34.45,2024-01-15,02:01:55
"Bob",30,"New York, \"USA\"",55.3,2025-02-14,15:18:55
"Alice2",25,"Paris",34.45,2024-01-15,02:01:55
"Bob2",30,"New York, \"USA\"",55.3,2025-02-14,15:18:55
"Alice3",25,"Paris",34.45,2024-01-15,02:01:55
"Bob3",30,"New York, \"USA\"",55.3,2025-02-14,15:18:55
"Alice4",25,"Paris",34.45,2024-01-15,02:01:55
"Bob4",30,"New York, \"USA\"",55.3,2025-02-14,15:18:55

```

```python

df = pd.read_csv("file3.csv", 
                 dtype={"name": "string", 
                        "age": "int8", 
                        "city": "string", 
                        "price": "float32"}, 
                skiprows=2, 
                nrows=3)
print(df)

```

Output.

```

    Bob  30  New York, \USA\""   55.3  2025-02-14  15:18:55
0  Alice2  25              Paris  34.45  2024-01-15  02:01:55
1    Bob2  30  New York, \USA\""  55.30  2025-02-14  15:18:55
2  Alice3  25              Paris  34.45  2024-01-15  02:01:55

```

It works

Note that the `header` is also skipped, which technically makes the new header the third line.

We can think of `skiprows` on being on the raw data (minus `header`) perspective.

We can also set `skiprows` to a size 2 tuple containing the range to not ingest.

```python

df = pd.read_csv("file3.csv", 
                 dtype={"name": "string", 
                        "age": "int8", 
                        "city": "string", 
                        "price": "float32"}, 
                 skiprows=range(1,3), 
                 nrows=3)
print(df)

```

Output

```

    name  age               city      price       date1     date2
0  Alice2   25              Paris  34.450001  2024-01-15  02:01:55
1    Bob2   30  New York, \USA\""  55.299999  2025-02-14  15:18:55
2  Alice3   25              Paris  34.450001  2024-01-15  02:01:55

```

Therefore `skiprows=2` is equivalent to `range(0, 2)`.

Those are also equivalent.

```python

df = pd.read_csv("file3.csv", 
                 dtype={"name": "string", 
                        "age": "int8", 
                        "city": "string", 
                        "price": "float32"}, 
                 skiprows=[1, 2], 
                 nrows=3)

```

And,

```python

df = pd.read_csv("file3.csv", 
                 dtype={"name": "string", 
                        "age": "int8", 
                        "city": "string", 
                        "price": "float32"}, 
                 skiprows=range(1, 3), 
                 nrows=3)


```

Output.

```

    name  age               city      price       date1     date2
0  Alice2   25              Paris  34.450001  2024-01-15  02:01:55
1    Bob2   30  New York, \USA\""  55.299999  2025-02-14  15:18:55
2  Alice3   25              Paris  34.450001  2024-01-15  02:01:55

```

Agian,because those containers maintain an order of their elements and are iterable.

#### Partial reads (Columns)

You can also specify the columns you want to read with `usecols`.

Like `usecols=["col1", "col2"]` or with indices `usecols=[1, 4]`.

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

Then, this doesn't work when the header containing the column name used in `usecols` is missed.

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

--> Error because unable to find the columnname at `row = 1`, this is expected because column names are at `row = 0`.

Note that `usecols` does not reorder cols.

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

Because it just doesn't care about the names.

(columns names = values here)

Quote handling is also very important !

Take this file for eample:

```

name,age,city
"Alice",25,"Paris"
"Bob",30,"New York, USA"

```

The column separator is `,`, but we also find it inside the values for `"City"`, then we specify `quote="\""` (default values).

```pyhon

data = pd.read_table("file2.csv", 
                     sep=",", 
                     encoding="latin1", 
                     header=0, 
                     quotechar="\"")

```

If your quoted values have quote themselves, be sure to double quote them, that is the `CSV` standard.

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

Escape character is also something very important.

Look, even if your CSV is single quoting inside quoted value, you can put `escapechar="\\"` which tells the `pandas` Df engine to threat the next character to `\` as a normal character even if it has a special meaning (quotes for example).

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

#### Export

Straigtforward:

```python

df.to_csv("file_out.csv")

```

Or set `index = False` to not write indices into the file.

### `FWF` file

It is a file with no delimiters but each column is spaced by a constant space.

Example file:

```

name      ageLocation date
Alice     025Paris    2025-05-16 
Bob       030London   2025-04-16
Charlie   035New York 2026-12-17

```

1. `name` -> 10 chars (if shorter than 10 chars, then white space) 

2. `age` (3 characters) City

3. `city` -> Same as Name

3. `date` -> Same as Name

```python

df = pd.read_fwf("file.fwf")
print(df)

```

Output:

```

      name  ageLocation        date
0    Alice     025Paris  2025-05-16
1      Bob    030London  2025-04-16
2  Charlie  035New York  2026-12-17

```

Ha, it looks that it did not infere well spacing between Age and City, which is normal since there is not obvious spacing, they are contiguous.

Then we can specif ourselves with `colspecs` option.

```pyhton

df = pd.read_fwf("file.fwf", 
                 colspecs=[(0,10), (10,13), (13,22), (22,32)])

print(data)

```

Output:

```

      name  ageLocation        date
0    Alice     025Paris  2025-05-16
1      Bob    030London  2025-04-16
2  Charlie  035New York  2026-12-17

```

It also supports `skiprows`, `nrows`, `parse_dates` and `usecols`.

You also note that we do not need any `quotechar` neither `escapechar`, because here you literally provide the scheme where a column have a **constant** width.

Example.

```python

df = pd.read_fwf("file.fwf", 
                 colspecs=[(0,10), (10,13), (13,22), (22,32)], 
                 usecols=["date", "age", "Location"], 
                 skiprows=range(1, 2), 
                 nrows=3,
                 parse_dates=["date"])
print(df)

```

Output.

```

   age  Location       date
0   30    London 2025-04-16
1   35  New York 2026-12-17

```

#### Export

`pandas` does not expose a `.to_fwf()` method, so we have to use the `.to_string()` method that creates a string representation of our `pd.DataFrame`:

```python

with open("file_out.fwf", "w", encoding="utf-8") as f:
    f.write(df.to_string(index = False))

```

Take a look at the string representation of our `pd.DataFrame`:

```python

>>> df.to_string(index = False)

'  name  age              city  price      date1    date2\n Alice   25             Paris  34.45 2024-01-15 02:01:55\n   Bob   30 New York, \\USA\\""  55.30 2025-02-14 15:18:55\nAlice2   25             Paris  34.45 2024-01-15 02:01:55\n  Bob2   30 New York, \\USA\\""  55.30 2025-02-14 15:18:55\nAlice3   25             Paris  34.45 2024-01-15 02:01:55\n  Bob3   30 New York, \\USA\\""  55.30 2025-02-14 15:18:55\nAlice4   25             Paris  34.45 2024-01-15 02:01:55\n  Bob4   30 New York, \\USA\\""  55.30 2025-02-14 15:18:55'

```

### `JSON`

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

But here is the thing, we can avoid the extra step of constructing an intermediate `pd.DataFrame` object.

We just load raw `JSON` file and ten apply normalization.

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

Then we still load the file with `json.load()`, but after we specify the record path in the normalization.

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

Note that `.read_json()` does not have `usecols` neither `skiprows` arguments.

I'm pretty sure it is possibe to at least implement a `usecols` feature, but it requires to work on the `json` parsing engine.

So, a common pattern, is to drop columns afterward (for `usecols`):

```python

df.drop(columns = ["col2", "col5"], inplace = True)

```

Or to filter afterward (for `skiprows`).

But the ingestion cost is already paid...

#### Export

The export to a `JSON` filetype is staightforward:

```python

df.to_json("file_out.json")

```

By default this will output in the following `orient = "columns"` format:

```

{
  column_name: {
    index_label: value
  }
}

```

When you set it as `orient = "records"`:

```

[
  {"name": "Alice", "age": 25, "city": "Paris"},
  {"name": "Bob", "age": 30, "city": "London"},
  {"name": "Charlie", "age": 35, "city": "New York"}
]

```

But here I added the breaklines at the end, but this is really not the case, so to have a nice human-readable `JSON` file export, use `lines=True`, because it defaults to `False`.

And to have a really good looking file, use `indent=2`, it will add 2 space for each intrication level, so we end up with:

```

  {
    "name":"Alice",
    "age":25,
    "city":"Paris"
  }

  {
    "name":"Bob",
    "age":30,
    "city":"London"
  }

  {
    "name":"Charlie",
    "age":35,
    "city":"New York"
  }

```

And when you have date columns, don't forget to set `date_format="iso"`.

### `HTML` table, Seriously

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

Here you'll read as a `table`. 

A `table` is a list of `pd.DataFrame` (because an `HTML` file can contain multiple `pd.DataFrame` like the one we see).

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

Note, that `"file.html"` is obviously a string representing a filename, but you can even pass raw string vlue directly representing data.

In order to do this we have to make the string behave like a file using `StringIO` from `io`.

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

#### Export

Simple enough:

```python

df.to_html("file_out.html")

```

Or with `index = False`.

You can also tell to use a specific `CSS` class:

```python

df.to_html("file_out.html", classes = "my-table-class")

```

This will just generate the `table`, then for a full `html` page wrapps it into a html page string like that:

```python

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DataFrame export</title>
</head>
<body>
{df.to_html(index=False)}
</body>
</html>
"""

with open("output.html", "w", encoding="utf-8") as f:
    f.write(html)

```

Also, letting the output filename argument to `None` will return a string of what would be written in the file:

```python

html = df.to_html(index = false)

with open("file_out.html", "w", encoding = "utf-8") as f:
    f.write(html)

```

### `PARQUET` file.

You know the one that stores data compressed and as:

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

Really good for ingestion speed, it is a no match agains `CSV` (no byte jumps + SIMD friendly for ingestion).

```python

df = read_parquet("example.parquet")

```

--> You can also set `columns=["col1", "col2"]` or `columns=[5, 3, 5]` for example, the equivalent for `usecols` in `.read_csv()`.

--> `use_threads=True`


Its super-power are **filters** while ingesting data.

```python

df = pd.read_parquet(
    "data.parquet",
    filters=[("age", ">", 30)]
)

```

#### PARQUET Exports

You can create a directory hierarchy based on the values of a chosen column. --> Partitions

Example:

```python

import pandas as pd

df = pd.DataFrame({
    "country": ["FR", "FR", "EN", "ESP"],
    "PIB": [11, 10.5, 9, 7],
    })

df.to_parquet("dataset_parquet/", partition_cols=["country"])

```

Then we have:

```

datase_parquet/
     'country=EN'/
        0931188c4d154d15bb5be538bf3b91c5-0.parquet
     'country=ESP'/
        0931188c4d154d15bb5be538bf3b91c5-0.parquet
     'country=FR'/
        0931188c4d154d15bb5be538bf3b91c5-0.parquet

```

The filenames are:

```

ID_AUTO_GENERATED-CHUNK.parquet

```

Here you see the ids are the same for everyone, because they come from the same write job lauched by the Arrow engine.

I can retry it and now I have.

```

datase_parquet/
     'country=EN'/
        0931188c4d154d15bb5be538bf3b91c5-0.parquet
        aaad8aa9c4ae4446b3dbaf8135119fb9-0.parquet
     'country=ESP'/
        0931188c4d154d15bb5be538bf3b91c5-0.parquet
        aaad8aa9c4ae4446b3dbaf8135119fb9-0.parquet
     'country=FR'/
        0931188c4d154d15bb5be538bf3b91c5-0.parquet
        aaad8aa9c4ae4446b3dbaf8135119fb9-0.parquet

```

Now, I want to read it!

```pyton

df = pd.read_parquet("dataset_parquet/", 
                    filters=[("country", "in", ["FR", "ESP"])]) # predicate
print(df)

```

Output.

```

    PIB country
0   7.0     ESP
1   7.0     ESP
2  11.0      FR
3  10.5      FR
4  11.0      FR
5  10.5      FR

```

##### Predicates Architecture -> Search Complete

Note that predicate is always:

```

("column", "operator", value)

```

Btw, what is the architecture of predicates in this argument ?

It is just:

```

filters = [
    [ (cond1), (cond2) ],   # AND group
    [ (cond3) ]             # OR with above
]

```

Here, yo have **AND GROUP**, and predicates all predicates are in **OR GROUP**.

So you effectively have a search-complete predicate.

```

OR(AND(p1, p2), AND(p3), AND(p4)...)

```

And you can put multiple predicates inside the list obviously.

That's the definition of **Disjunctive Normal Form**.

#### Going back to partitions

What happen to the filestructure if I partition accross multiple columns ?

```python

import pandas as pd

df = pd.DataFrame({
    "country": ["FR", "FR", "EN", "ESP"],
    "location": ["A", "B", "B", "A"],
    "PIB": [11, 10.5, 9, 7],
    })

df.to_parquet("dataset_parquet2/", 
              partition_cols=["country", "location"])

```

Output.

```

datase_parquet2/
     'country=EN'/
        'location=B'
            8e46fe4c05204c5b896a1b973883594c-0.parquet
     'country=ESP'/
        'location=A'
            8e46fe4c05204c5b896a1b973883594c-0.parquet
     'country=FR'/
        'location=A'
            8e46fe4c05204c5b896a1b973883594c-0.parquet
        'location=B'
            8e46fe4c05204c5b896a1b973883594c-0.parquet

```

Does the filestructure output depends on the order of `partition_cols` ?

Lets' find out !

```python

import pandas as pd

df = pd.DataFrame({
    "country": ["FR", "FR", "EN", "ESP"],
    "location": ["A", "B", "B", "A"],
    "PIB": [11, 10.5, 9, 7],
    })

df.to_parquet("dataset_parquet3/", partition_cols=["location", "country"])

```

Output.

```

datase_parquet2/
   'location=A'
        'country=ESP'/
            8e46fe4c05204c5b896a1b973883594c-0.parquet
        'country=FR'/
            8e46fe4c05204c5b896a1b973883594c-0.parquet
   'location=B'
        'country=EN'/
            8e46fe4c05204c5b896a1b973883594c-0.parquet
        'country=FR'/
            8e46fe4c05204c5b896a1b973883594c-0.parquet

```

--> Yess

#### Chunks

The suffix:

```

ID-0.parquet
ID-1.parquet

```

appears when:

- multiple files are written in the same batch

- often via parallelism or batching

#### PARQUET and Pruning for predicates while reading

`PARQUET` has the concet of row groups.

It is a group of rows from which you can decide the size.

Each row groups exposes some metadata about their columns, like `min`, `max`...

Then when we use filters while reading a `PARQUET` file, the engine will optimize its ingestion time by skipping unnecessary data.

Example:

```

RowGroup1: colB:
            min: 2, max: 6
[...]
...

RowGroup2: colB:
            min: 6, max: 9
[...]
...

RowGroup3: colB:
            min: 9, max: 12
[...]
...

```

And the filter is `[[("colB", ">=", 7), ("colB", "<", 8)]]`.

Then it will check relevant metadata for `RowGroup1`, jump it, do the same for `RowGroup2` -> ingest the data, check relevant metadata for `RowGroup3`, jump it -> end.

But, take a higher picture !

It also does it file-wise, concerning the file partitions.

Then, if you know that your data pipeline will often do a certain type of query on some columns, be aware to well partition the data by the queried columns.

To control `row_group` size, you must import `pyarrow`.

In order to make this work, of course you have to sort your data by queried columns first before writing it.

If not, the engine won't recognize a sorting patern and will load all before filtering internally.

Example.

```python

import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

set_country = ["FR", "EN", "ESP"]
set_location = ["A", "B"]

df = pd.DataFrame({
    "country": np.random.choice(set_country, 100_000),
    "location": np.random.choice(set_location, 100_000),
    "PIB": np.random.normal(3, 15, 100_000),
    })

df = df.sort_values("PIB", ascending=False) # don't forget to sort it
df["PIB_bucket"] = (df["PIB"] // 10) * 10

table = pa.Table.from_pandas(df)

pq.write_to_dataset(table,
                    root_path = "dataset_parquet4/",
                    partition_cols=["PIB_bucket"],
                    row_group_size=5_000
                    )

df = pd.read_parquet("dataset_parquet4/",
                     columns = ["country", "PIB"],
                     filters=[
                              [
                                ("PIB_bucket", ">=", 10),
                                ("PIB_bucket", "<", 20),
                                ("PIB", ">=", 11), 
                                ("PIB", "<=", 13)
                              ]
                             ]
                     )

print(df)

```

File structure output.

```

dataset_parquet4
├── PIB_bucket=0
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=-10
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=10
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=-20
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=20
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=-30
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=30
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=-40
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=40
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=-50
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=50
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=-60
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
├── PIB_bucket=60
│   └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet
└── PIB_bucket=70
    └── 971ab64de516473ba7fad4bee55ee5c0-0.parquet

```

Output.

```

      country        PIB
46985     ESP  12.999798
99670      FR  12.999724
27864     ESP  12.999641
75344      FR  12.998913
19709      EN  12.997386
...       ...        ...
43699      EN  11.003076
48763      FR  11.002752
2161       EN  11.002653
32576      FR  11.002025
48103      EN  11.000283

```

Note that here, I created a column just for the file partition and query optimization (`PIB_bucket`).

So at ingestion time, the engine will skip entire files that are `PIB_bucket < 10` and `PIB_bucket > 20` and it will skip entire `row_groups` inside the matching files.

--> You can also put `columns=["col1", "col2"]` or `columns=[5, 3, 5]` for example

--> `use_threads=True` (in `pd.read_parquet()` and `pq.write_dataset()`).

For `pyarrow`, to set a maximum number of threads in the thread pool do the following:

```python

pa.set_cpu_count(N1)
pa.set_io_thread_count(N2)

```

And then the `pyarrow` operations that have `use_threads = True` will not get higher than the indicated threads.

Why is there 2 threads pools ?

There is one for CPU computations and another for IO operation.

### `FEATHER` format.

Same as `PARQUET` but not compressed by default -> quicker for ingesting and writing data.

For this one you'll also need to install `pyarrow`.

```bash

pip install pyarrow

```

It is a binary file too (like `PARQUET`) so I can not show it but I can make an export of an actualy understable data.

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

--> You can also set `columns=["col1", "col2"]` or `columns=[5, 3, 5]` for example (like for `PARQUET`).

--> `use_threads=True`

Cons compared to `PARQUET`.

While it is simpler and way faster for ingestion in general case, there is no ingestion filters on the fly and no automatic file partitions based on columns values.

All is stored in a single file, and it does not have metadata ence no `row_group` concept.

But, we can still do the big win thing !

File partitioning, manually.

Technically you can apply this method with `CSV`, `JSON`, `FWF`...

Example:

```python

import pandas as pd
import numpy as np
import os, shutil

set_country = ["FR", "EN", "ESP"]
set_location = ["A", "B"]

df = pd.DataFrame({
    "country": np.random.choice(set_country, 100_000),
    "location": np.random.choice(set_location, 100_000),
    "PIB": np.random.normal(3, 15, 100_000),
    })

df = df.sort_values("PIB", ascending=False)
df["PIB_bucket"] = (df["PIB"] // 10) * 10

f = "dataset_feather"

# os.rmdir(f) # only empty dirs lol

shutil.rmtree(f)
os.mkdir(f)

for chk in df["PIB_bucket"].unique():
    cur_df = df[df["PIB_bucket"] == chk]
    cur_df.to_feather(f"{f}/data={chk}.feather")

```

Then output is:

```

dataset_feather/
├── data=0.0.feather
├── data=-10.0.feather
├── data=10.0.feather
├── data=-20.0.feather
├── data=20.0.feather
├── data=-30.0.feather
├── data=30.0.feather
├── data=-40.0.feather
├── data=40.0.feather
├── data=-50.0.feather
├── data=50.0.feather
├── data=-60.0.feather
├── data=60.0.feather
└── data=70.0.feather

```

-> Good pruning

### You know what ?

`PARQUET` should not be able to have the monopole on file partitioning over data.

So let's reimplement this part at another abstraction level.

First, ingestion time.

We define a function that recursively list files that respect a condition defined in a function `d_mask`.

```python

def list_files_rec(dr: str, 
                   d_mask) -> list[str]:
    rtn_lst = []

    try:
        for name in os.listdir(dr):
            cur = os.path.join(dr, name)
            if os.path.isdir(cur) and not os.path.islink(cur):
                rtn_lst.extend(list_files_rec2(cur, d_mask))
            elif d_mask(cur):
                rtn_lst.append(cur)
    except PermissionError:
        pass
    return rtn_lst

```

We could have replace the:

```python

rtn_lst.extend(list_files_rec2(cur, f_mask))

```

with simply:

```python

rtn_lst = rtn_lst + list_files_rec2(cur, rgx)

```

But it would be less performant because `Python` has to create a new list each time (because of `lst3 = lst1 + lst2`, not a simple proxy as just `lst2 = lst1`) and even if the strings are not copied, the reference are (and the new list has to allocate to store the references).

While using the `.extend()` method makes the intent clearer and is exactly what we need here.

We also need to define a mini-parser that will understand `filters` semantic:

```python

def d_satisfy(f: str, filters: list | None) -> bool:
    for cond in filters: 
        for col, op, val in cond:  
            ok = True
            cur = get_var(f, col)
            if cur is None:
                ok = False
                continue

            # if just equality cheks, then no need to convert to a float
            if op != "=" and op != "!=":

                try:
                    cur = float(cur)
                except (TypeError, ValueError) as e:
                    raise ValueError(f"Can't convert {cur!r} to float") from e

            match op:
                case ">":   ok = (cur > val)
                case ">=":  ok = (cur >= val)
                case "=":   ok = (cur == val)
                case "!=":   ok = (cur != val)
                case "<=":  ok = (cur <= val)
                case "<":   ok = (cur < val)
                case _:     ok = False

            if ok:
                break

        if ok:
            return True

    return False

```

That will be the the value of `d_mask`.

`get_var()` extracts the value of the current partitioned column:

```python

def get_var(path: str, var: str) -> str | None:
    for part in path.split("/"):
        if part.startswith(var + "="):
            return part.split("=", 1)[1]
    return None

```

Then we plug this together.

```python

def read_partitions(f: str,
                    *,
                    filters: list | None = [],
                    columns: list | None = None,
                    read_method) -> pd.DataFrame:

    filters = [] if filters is None else filters

    lst_files = list_files_rec(f, 
                               lambda p: d_satisfy(p, filters)
                               )
    if not lst_files:
        return pd.DataFrame()

    #rtn_df = read_method(lst_files[0])
    #for f in lst_files[1:]:
    #    cur_df = read_method(f)
    #    rtn_df = pd.concat([rtn_df, cur_df], axis = 0)
    # or in ONE allocation for the concatenation
    dfs = [read_method(f) for f in lst_files]
    rtn_df = pd.concat(dfs, axis=0)

    return rtn_df

```

Here, the `*` in the args, just mean that after argument `f: str`, each argument must be named, so no positional argument, only named (`columns=[...]`).

So far so good.

Now, writing.

We'll need to precompute all the boolean masks.

We'll encode all the data as we need in order to do this as a 2 dimensional list:

```

[
  COL1_UNIQUE_VALUES,
  COL2_UNIQUE_VALUES,
  ...
]

```

expanding to, for example:

```

[
  [1,2,3,4],
  ["A", "B"]
]

```

So now a little bit of combinatorics (manualy because we all love algos).

In the example the total amount of al combinations is 4 * 2 = 8.

Then we must have a function that takes an `int` between 0 and `max-comb-value`, gives the index for each column.

```

def get_ids(n: int, lst_nb: list) -> list:
    ids = []
    for base in reversed(lst_nb):
        ids.append(n % base)
        n //= base
    return list(reversed(ids))

```

See it as unit convertion walker.

It is like a clock, you got hours, minutes, seconds.

Here, it's the same, all units are side to side from largest to smallest.

We need to convert it first in the smallest unit until to the largest one in order to preserve the values for all units.

That's why you see the `reverse` because in the list, units are descendly ordered.

And after, that's just:

```python

n % base

```

--> How many of this `base` unit `n` is at ? 

After, we convert `n` to this unit.

```python

n // base

```

So next iteration with the next bigger unit, we can do the convertion.

It is in fact:

--> How many of the next smaler unit i'm made of ?

It's like.

```

12 days 3 hours 23 minutes 34 seconds = (12 * 24 * 60 * 60) + (3 * 60 * 60) + (23 * 60) + 34 = 1049014

```

You have only the result: `1049014` and yu ask yoursef, by how many days, hours, minutes and seconds it is made ?

Or in another term:

```
[days, hours, minutes, seconds]
```

You want index for each position.

How many seconds ? -> `1049014 % BASE_SECOND` -> `1049014 % 60` = `34`

Convertion into minutes -> `1049014 // 60` = `17483`

How many minutes ? -> `17483 % BASE_MINUTE` -> `17483 % 60` = `23`

Convertion into hours -> `17483 // 60` -> `291`

How many hours ? -> `291 % BASE_HOUR` -> `291 % 24` = `3`

Final convertion into hours -> `291 // 24` = `12`

Now, we plug that into a function that will (pre)compute all predicates we need for the next file partition filtering.

```python

def make_predicates(df: pd.DataFrame, 
                    dct: dict) -> list:
    lst = []
    lst_nb = []
    max_value = 1

    for k in dct.keys():
        cur_lst = []
        for vl in dct[k]:
            cur_lst.append(df[k] == vl)
        lst.append(cur_lst)
        lst_nb.append(len(dct[k]))   
        max_value *= len(dct[k])

    rtn_lst = []

    cnt = 0
    while cnt < max_value:
        ids = get_ids(cnt, lst_nb)

        cur_sr = pd.Series(True, index=df.index)

        for i in range(len(ids)):
            cur_sr &= lst[i][ids[i]]   

        rtn_lst.append(cur_sr)         
        cnt += 1

    return rtn_lst

```

In the first step, we just build the data we need, such as the fundamental columns boolean mask `cur_lst.append(df[k] == vl)` and making them correspond to a number `lst_nb.append(len(dct[k))` being the number of unique values inside each column. (discussed later in `write_partitions(...)`)

In the second phase, we get the indices of each fundamental boolean mask with `ids = get_ids(cnt, lst_nb)`, and we iterate on each of these columns fundamental boolean mask to get the resulting boolean mask for the combination found at `cnt`.

Note: If the number of unique values were constant accross keys, I could simplify it as, in the first phase:

```python

max_value = CONSTANT_KEY_NB * len(dct)

lst_nb = [ CONSTANT_KEY_NB ] * len(dct)

for k in dct.keys():
    for vl in dct[k]:
        lst.append(df[k] == vl)


```

And in the second phase:

```python

for i in range(len(ids)):
    cur_sr &= lst[i * CONSTANT_KEY_NB + idx[i]]

```

To save some mental sanity, we can just rely on `product` from `itertools` pkg to build cartesian product.

```python

from itertools import product

def make_predicates2(df: pd.DataFrame, dct: dict) -> list:
    keys = list(dct.keys())
    all_combinations = product(*(dct[k] for k in keys))

    predicates = []

    for combo in all_combinations:
        mask = pd.Series(True, index=df.index)
        for k, v in zip(keys, combo):
            mask &= (df[k] == v)
        predicates.append(mask)

    return predicates

```

`product()` does:

```python

for i in product([1,2,3], ["A", "B"]): print(i)

```

Output:

```

(1, 'A')
(1, 'B')
(2, 'A')
(2, 'B')
(3, 'A')
(3, 'B')

```

The `*` is weird, but it just means unpacking a tuple to fit the args, look:

```python

def f(a, b):
    print(a, b, c)

f((2, 3, "DD"))

```

Output:

```

2 3 DD

```

But here we'll continue with the original one.

Finally, plugging this together we got:

```python

def write_partitions(f: str,
                     df: pd.DataFrame,
                     *,
                     partitions: list,
                     write_method,
                     ext: str) -> None:

    shutil.rmtree(f, ignore_errors=True)
    os.mkdir(f)

    f += "/"
    dct = {}
    max_value = 1
    lst_nb = []
    for cl in partitions:
        cur_unique = df[cl].unique()
        lst_nb.append(len(cur_unique))
        max_value *= len(cur_unique)
        dct[cl] = cur_unique
    lst_predicates = make_predicates(df, dct)
    
    cnt = 0
    while cnt < max_value:
        ids = get_ids(cnt, lst_nb)
        cur_f = f

        for i in range(len(partitions)):
            k = partitions[i]
            cur_f += f"{k}={dct[k][ids[i]]}/"
        os.makedirs(cur_f, exist_ok=True) # equivalent of bash `mkdir -p`

        cur_f += "data" + ext
        cur_df = df[lst_predicates[cnt]]
        write_method(cur_df, cur_f)
        cnt += 1

```

In the first phase, we see the creation of `dct`, the dict passed to `make_predicates(...)` mapping each col to all its unique values.

And you see ?

I recomputes `lst_nb` because I need it too inside this function (for `get_ids()`, the differents `ids` are also something I could return in `make_predicates`).

So yess, I could just return it (by ref) from `make_predicates(...)` instead of allocating the same list inside `write_partitions(...)` but I wanted a good separation of concern even if it is justified to do it there...

Because yess , list created inside a function does not disapear, its local variable may, but not its memory, look at this example:

```python

def fun():
    x = [1, 2, 3]
    return x

lst = fun()
lst.append(4)

print(lst)
# [1, 2, 3, 4]

```

After `fun()` finishes, its local variable `x` disappears, but the list itself does not disappear because `lst` now references it.

As you probably noticed second phase is for generating the file partition with asociated data.

```python

cur_f += "data" + ext
cur_df = df[lst_predicates[cnt]]

```

Output is:

```

dataset_feather/
├── country=EN
│   ├── PIB_bucket=0.0
│   │   └── data.feather
│   ├── PIB_bucket=-10.0
│   │   └── data.feather
        ...
├── country=ESP
│   ├── PIB_bucket=0.0
│   │   └── data.feather
│   ├── PIB_bucket=-10.0
│   │   └── data.feather
│   ├── PIB_bucket=10.0
│   │   └── data.feather
        ...
└── country=FR
    ├── PIB_bucket=0.0
    │   └── data.feather
    ├── PIB_bucket=-10.0
    │   └── data.feather
    ├── PIB_bucket=10.0
    ...

```

But wait, maybe that's too much complex and sub-optimal.

And yess, it is.

Here it's generating all combinations, even for the ones that corresponds to zero rows.

If only we got an algorithm that could generate the combinations from actual data and not just from supposition of what data can be !

Have you heard about `grouping by X, Y, Z and ...`.

Yess, that's exactly the algorithm that we need here, and straight up from `pandas`.

```python

def write_partitions2(f: str,
                      df: pd.DataFrame,
                      *,
                      partitions: list,
                      write_method,
                      ext: str) -> None:

    shutil.rmtree(f, ignore_errors=True)

    for keys, subdf in df.groupby(partitions):
        if not isinstance(keys, tuple):
            keys = (keys,)

        cur_f = f + "/"
        for k, v in zip(partitions, keys):
            cur_f += f"{k}={v}/"

        os.makedirs(cur_f, exist_ok=True)

        write_method(subdf, cur_f + "data" + ext)

```

I just want to emphase what `pd.groupby(...)` returns.

```python

df = pd.DataFrame({
            "c1": [1, 2, 1, 1, 2, 3], 
            "c2": ["a", "c", "b", "b", "c", "a"], 
            "c3": [22, 17, 33, 7, 4, 8]
                }
)

for (k, subdf) in df.groupby(["c1", "c2"]): print(k)

```

Output.

```

(1, 'a')
(1, 'b')
(2, 'c')
(3, 'a')

```

Here are the key identifiers of each sub-dataframe that have the associated rows.

Now let's print the sub-datarames.

```python

for (k, subdf) in df.groupby(["c1", "c2"]): print(subdf, "\n")

```

Output.

```

   c1 c2  c3
0   1  a  22

   c1 c2  c3
2   1  b  33
3   1  b   7

   c1 c2  c3
1   2  c  17
4   2  c   4

   c1 c2  c3
5   3  a   8

```

Now you get what it is.

**Only groups that actually exist are preserved**


Now, it's time to use all those implementations.

First, we create a reproductible (`rng = np.random.default_rng(42)`) test dataset.

```python

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

```

Then, the write is just:

```python

write_partitions2("dataset_feather", 
                  df,
                  partitions=["country", "PIB_bucket"],
                  write_method=pd.DataFrame.to_feather,
                  ext=".feather")

```

Output is:

```

dataset_feather/
├── country=EN
│   ├── PIB_bucket=0.0
│   │   └── data.feather
│   ├── PIB_bucket=-10.0
│   │   └── data.feather
│   ├── PIB_bucket=10.0
│   │   └── data.feather
│   ├── PIB_bucket=-20.0
│   │   └── data.feather
│   ├── PIB_bucket=20.0
│   │   └── data.feather
│   ├── PIB_bucket=-30.0
│   │   └── data.feather
│   ├── PIB_bucket=30.0
│   │   └── data.feather
│   ├── PIB_bucket=-40.0
│   │   └── data.feather
│   ├── PIB_bucket=40.0
│   │   └── data.feather
│   ├── PIB_bucket=-50.0
│   │   └── data.feather
│   ├── PIB_bucket=50.0
│   │   └── data.feather
│   ├── PIB_bucket=-60.0
│   │   └── data.feather
│   ├── PIB_bucket=60.0
│   │   └── data.feather
│   ├── PIB_bucket=-70.0
│   │   └── data.feather
│   └── PIB_bucket=70.0
│       └── data.feather
├── country=ESP
│   ├── PIB_bucket=0.0
│   │   └── data.feather
...


47 directories, 43 files

```

And ingestion is:

```python

df = read_partitions("dataset_feather",
                     filters=[
                              [
                                ("PIB_bucket", ">=", 10),
                                ("country", "=", "FR"), 
                              ]
                             ],
                     columns = None,
                     read_method = pd.read_feather
)

```

Output:

```

      country location        PIB  PIB_bucket
68154      FR        A  39.969140        30.0
76813      FR        B  39.961713        30.0
95196      FR        A  39.942438        30.0
19172      FR        A  39.911750        30.0
55985      FR        B  39.901974        30.0
...       ...      ...        ...         ...
91438      FR        A  40.084317        40.0
52215      FR        B  40.077076        40.0
77656      FR        A  40.065780        40.0
94928      FR        B  40.054049        40.0
51555      FR        A  40.026043        40.0

[10644 rows x 4 columns]

```

We can even copare the performance difference between the 2 `write_partitions()` and `write_partitions2()`:

```python

strt = time.time()

write_partitions("dataset_feather", 
                 df,
                 partitions=["country", "PIB_bucket"],
                 write_method=pd.DataFrame.to_feather,
                 ext=".feather")

end = time.time()

```

Output:

```

0.06887030601501465

```

Compared to:

```python

strt = time.time()

write_partitions2("dataset_feather", 
                  df,
                  partitions=["country", "PIB_bucket"],
                  write_method=pd.DataFrame.to_feather,
                  ext=".feather")

end = time.time()

```

Output:

```

0.04759383201599121

```

Which is expected because we skip the creation of directories for no existing data.

### DB Connectors

#### PostGreSQL

Install the binaries:

```bash

sudo apt install postgresql postgresql-contrib
sudo -u postgres pgsql

```

`postgresql-contrib` is a package that comes with various extensions that we won't discuss here, but we usually install it with `postgresql` (no bad surprises).

User and DB creation.

```

CREATE USER juju WITH PASSWORD 'password';

CREATE DATABASE test_db OWNED BY juju;

\c test_db; # Equivalent to USE test_db in MySQL

CREATE TABLE test_table (
    name VARCHAR(25), 
    age INTEGER CHECK (age >= 0), 
    city VARCHAR
);


```

Install the python connector:

```bash

pip install psycopg2-binary

```

Then here are the imports and setup:

```python

import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import time, io

engine = create_engine(
    "postgresql+psycopg2://juju:password@localhost:5432/test_db"
)

df = pd.read_sql_table("test_table", con = engine)

```

You see that `create_engine(...)` uses `psycopg2` connector.

We can even filter on the fly before ingestion:

```python

with engine.connect() as conn:
    out = pd.read_sql(
        text("SELECT * FROM table1 WHERE country = :country"),
        conn,
        params={"country": "FR"},
    )

```

`pd.read_sql` is a convenience wrapper that is either routed to `pd.read_sql_table()` or `pd.read_sql_query()`, example:

```python

pd.read_sql("test_table", con=engine)

```

Is routed to:

```python

pd.read_sql_table("test_table", con=engine)

```

While:

```python

pd.read_sql("SELECT * FROM test_table", con=engine)

```

Is routed to:

```python

pd.read_sql_query("SELECT * FROM test_table", con=engine)

```

You may see some cases where `con` just accepts the `engine` or the already opened connection `engine.connect()`, here the conection lifetime is explicit:

```python

with engine.conect() as conn:
   ...

# conn is closed here

```

We use this model for operations that should use the same conection (same semantic or are dependant).

For example:

```python

with engine.connect() as conn:
    df1 = pd.read_sql("SELECT * FROM table1", conn)
    df2 = pd.read_sql("SELECT * FROM table2", conn)

```

Or:

```python

with engine.connect() as conn:
    conn.execute(
        text("UPDATE table1 SET age = age + 1 WHERE country = :country"),
        {"country" : "FR"}
    )

    df = pd.read_sql("table1", conn)

```

And here is the export of a DataFrame:

```python

df = pd.DataFrame({
    "country": rng.choice(set_country, 100_000),
    "location": rng.choice(set_location, 100_000),
    "PIB": rng.normal(3, 15, 100_000),
})

df = df.sort_values("PIB", ascending=False)
df["PIB_bucket"] = (df["PIB"] // 10) * 10

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method="multi",
    chunksize=10_000, 
)

```

`chunksize=10_000` divides the data in batches of at most `10k` rows each.

Here, there are 10 batches.

And `method` determines the insertion strategy used -> It must "transpile" to PostgreSQL language (see later).

With `method="multi"`, each batch insertion is made with one `INSERT` command like so:

```

INSERT INTO table1 (country, location, PIB)
VALUES
    (V1, V2, V3),
    (V4, V5, V6)
    ...
    ;

```

Here it's clear, we have one `INSERT` call per batch which reduces the instruction number compared of what the more unpredictable and more DB connector, Postgre SQL dialect and configurations dependant the `method=None` can give.

It can be sometimes optimized, and sometimes not like this one:

```

INSERT INTO table1 (name, age) VALUES ('Alice', 25);
INSERT INTO table1 (name, age) VALUES ('Bob', 30);
INSERT INTO table1 (name, age) VALUES ('Charlie', 35);

```


Which leds to more back and forth between the DB connector and the DB engine.

But in modern `sqlalchemy`, we have some pretty interesting results look at that:

```python

strt = time.time()

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method="multi",
    chunksize=10_000, 
)

end = time.time()

```

Performs the operation in about `4.87 seconds` on my machine  compared to:

```python

strt = time.time()

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method=None,
    chunksize=10_000, 
)

end = time.time()

```

Performing the operation in about `1.14 seconds`.

Why is that ?

Because both must emit an equivalent SQL statements (at least in the behavior relative to the table) statement, but the way they do it differe.

First, SQLAlchemy works with an intermediate representation of the data to export.

And this intrmediate representation is key, because it's not the same across methods.

The pipeline is roughly:

```

pandas DataFrame
    |
    V
pandas extracts rows into Python-level values
    |
    V
pandas builds parameter dictionaries / row tuples
    |
    V
SQLAlchemy constructs an Insert statement representation
    |
    V
SQLAlchemy compiles or expands it for PostgreSQL
    |
    V
psycopg2 receives SQL + parameters
    |
    V
PostgreSQL

```

And here in the `Insert` statement creation, `"multi"` does create a huge expression tree while the optimized version chosen when the method is delegated to `.to_sql` (`None`) is to create a small expression and derives the SQL code from it.

We can implement a much simpler logic just copying the data from standard input.

For that we will create our custom method, it should construct a buffer csv formated of our `pd.DataFrame` we want to export and use it as standard input:

```python

import pandas as pd
import csv
from sqlalchemy import create_engine
from io import StringIO

engine = create_engine(
    "postgresql+psycopg2://juju:password@localhost:5432/test_db"
)

#
# Dataframe creation here
#

def copy_from_df(
                 pd_table, 
                 conn, 
                 keys, 
                 data_iter
                ):

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerows(data_iter)
    buffer.seek(0)

    raw_connection = conn.connection
    cursor = raw_connection.cursor()

    columns = ", ".join(f'"{column}"' for column in keys)

    cursor.copy_expert(
        f'COPY "{pd_table.name}" ({columns}) FROM STDIN WITH CSV',
        buffer,
    )

# And, we use it as:

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method=copy_from_df,
    chunksize=10_000, 
)

```

`buffer` is a `StringIO()` so it behaves like a file from the Python POV, but its content stay in RAM of course.

`data_iter` is an iterable yielding rows as a tuple, but for the `COPY` command, standard input must be csv formated.

So here how `csv.writerows`works:

```python

>>> buffer = StringIO()

>>> writer = csv.writer(buffer)

>>> writer.writerows([(1, 'A', "plm"), (2, 'B', "qs")])

>>> buffer.getvalue()
'1,A,plm\r\n2,B,qs\r\n1,A,plm\r\n2,B,qs\r\n'

```

Here the `.getvalue()` method returns the entire value of the buffer ignoring the position of the cursor, but some methods will start at the cursor position like `.read()`:

```python

>>> buffer.read()
''

```

Because hre the cursor is at the end of the buffer (we just have written in it with `writer.writerows(...)`).

So we must set the cursor back to its original position:

```python

>>> buffer.seek(0)
0

>>> buffer.read()
'1,A,plm\r\n2,B,qs\r\n'

```

Therefore, if you need to read a buffer content after writing in it, use `.seek(0)` on it or `.seek(N)` if `N` is the last knowk position before writing and you just want to read the new added part.

Let's see how well it performed:

```python

strt = time.time()

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method=copy_from_df,
    chunksize=10_000, 
)

end = time.time()

```

It performed the operation in: `0.20` seconds !

more than 5 times faster than the optimal chosen path with SQLAlchemy.

#### MySQL - MariaDB

Install the binary:

```bash

sudo apt install mysql-server
sudo mysql

```

User and DB creation.

```

CREATE DATABASE test_db;

CREATE USER 'juju'@'localhost' IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES ON mydb.* TO 'juju'@'localhost';

FLUSH PRIVILEGES;

EXIT;

```

Install the python connector:

```

pip install pymysql

```

And in the actual code, the only thing that differes is the connection:

```python

engine = create_engine(
    "mysql+pymysql://juju:password@localhost:3306/test_db",
    connect_args={
        "local_infile": True, # allow to load local files
    },
)

```

And also the copy from standard input is not directly possible with MySQL/MariaDB because it needs a file on disk (by providing the filepath) hence we need to create a temporary CSV file:

```python

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

```

In terms of execution time for:

```python

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method=None,
    chunksize=10_000,
)

```

And its `method="multi"` equivalent, we have the same  results than for Postgre connector variant (`psycopg2`).

But because of the overhead of creating a temporary file on disk, it is slower:

```python

start_write = time.time()

df.to_sql(
    "table1",
    engine,
    if_exists="replace",
    index=False,
    method=mysql_load_data_insert
)

end_write = time.time()

```

Takes `0.70` seconds for example (same dataset).

### Other notes

**All files can be remote on a server with `https://domainname.com/path-to-file`**

To read `xls`/`xlsx` files, you do it via `pd.read_excel("data.xlsx")` or `pd.read_excel("data.xls")`.

Select a sheet via `sheet_name="Sheet1"`or even multiple sheets `sheet_name=["Sheet1", "Sheet2"]`.

### Manualy ingest local data. (`pd.DataFrame()`)

####  Dict

```python
data = {
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35]
}

df = pd.DataFrame(data)
```

#### Even a list of Dicts

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

#### Lists of Lists

Here you encode the column name as the first value of each python list.

```python
data = [
    ["name", "Alice", "Bob", "Charlie"],
    ["age", 25, 30, 35]
]

df = pd.DataFrame(data)
```

Also, note that the only comon datastructure with wich we can not create a `pd.DataFrame` is the set (`{...}`), because they are unordered by default, so `pandas` says that because it can not respect the visual order of the elements, it refuses to create it and returns an error:

```python

>>> df2 = pd.DataFrame({'A' : {1, 2, 3}, 'B' : {4, 5, 6}})

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/frame.py", line 769, in __init__
    mgr = dict_to_mgr(data, index, columns, dtype=dtype, copy=copy)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/internals/construction.py", line 460, in dict_to_mgr
    return arrays_to_mgr(arrays, columns, index, dtype=dtype, consolidate=copy)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/internals/construction.py", line 118, in arrays_to_mgr
    arrays, refs = _homogenize(arrays, index, dtype)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/internals/construction.py", line 596, in _homogenize
    val = sanitize_array(val, index, dtype=dtype, copy=False)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/construction.py", line 656, in sanitize_array
    _sanitize_non_ordered(data)
  File "/home/juju/plot/menv/lib/python3.12/site-packages/pandas/core/construction.py", line 715, in _sanitize_non_ordered
    raise TypeError(f"'{type(data).__name__}' type is unordered")
TypeError: 'set' type is unordered

```

While it works with list as seen before, but even with tuples:

```python

>>> df2 = pd.DataFrame({'A' : (1, 2, 3), 'B' : (4, 5, 6)})
>>> df2
   A  B
0  1  4
1  2  5
2  3  6

```

Quick remainder on the diferences between lists, tuples and sets.

Because this is not a question of: "one should have the same type values in it like np.ndarray requires"

And also all are iterable:

```python

>>> for a in {1, 2, 3}: print(a)
...
1
2
3

>>> for a in {1, 2, "3"}: print(a)
...
1
2
3

>>> for a in {1, 2, "A"}: print(a)
...
1
2
A

>>> for a in {"A", 2, 1}: print(a)
...
1
2
A

>>> for a in (1, 2, 3): print(a)
...
1
2
3

>>> for a in (1, 2, "3"): print(a)
...
1
2
3
>>> for a in [1, 2, "3"]: print(a)

...
1
2
3
>>> for a in [1, 2, 3]: print(a)
...
1
2
3

```

All works, but have you seen the difference in elements order here ?

```python

>>> for a in {1, 2, "A"}: print(a)
...
1
2
A

>>> for a in {"A", 2, 1}: print(a)
...
1
2
A


```

This is right, as written before `set` are is not ordered, hence we do not have random access on it:

```python

>>> {1, 2}[0]

```

There is more:

```python

>>> (1, 2, 3)[0] = 11

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'tuple' object does not support item assignment

>>> [1, 2, 3][0] = 11

```

`tuple` is imutable

A list is:

- ordered
- mutable
- sequence-like
- allows duplicates

A tuple is:

- ordered
- immutable
- sequence-like
- allows duplicates

A set is:

- unordered
- mutable
- not sequence-like
- does not allow duplicates
- optimized for membership testing

For example, this is why when you create a `numpy.ndarray` with a `set`, it considers it as a scalar, so returns a `numpy.ndarray` of size 1 and not a standard `int64`:

```python

>>> np.array({1, 2, 3})
array({1, 2, 3}, dtype=object)

>>> np.array({1, 2, 3}).size
1

>>> np.array({1, 2, 3}).dtype
dtype('O') # object type

```

Btw, consecutives `numpy.ndarray` auto flatten:

```python

>>> np.array(np.array({1, 2, 3})).shape
()
>>> np.array(np.array({1, 2, 3})).dtype
dtype('O')

```

Also, this array has a dimension of 0, therefore it behaves a bit like a scalar even if it is an array.

Here we compute the union as we would do it on raw `sets`.

```python

>>> np.array({1, 2, 3}) | np.array({1, 2, 4})
{1, 2, 3, 4}

```

Technically, we need to call the `.item()` method to unwrapp the inner object, but in this case it automaticaly do it, but we still need it normaly:

```python

>>> np.array({1, 2, 3}).item().union({4})
{1, 2, 3, 4}

>>> np.array({1, 2, 3}).union({4})

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'numpy.ndarray' object has no attribute 'union'

```

This also works while the right `numpy.ndarray` is obviously 1D, but because it just has one element then it is treated as 0D for this method:

```python

>>> np.array({1, 2, 3}) | np.array([{1, 2, 4}]).item()

{1, 2, 3, 4}

>>> np.array([{1, 2, 4}, {33, 22}]).ndim

1

```

Because it can safely extract the element for th method, while this doesn't work:

```python

>>> np.array([{1, 2, 4}, {33, 22}]).item()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: can only convert an array of size 1 to a Python scalar

```

### HDF5

### `fixed` flavor

`HDF5` stands for Hierarchical Data Format version 5. 

It is a binary file format designed to store large, structured scientific or numerical datasets.

Unlike `CSV`, an `HDF5` file can contain many objects organized like folders and files:

```

data.h5
├── experiments
│   ├── experiment_1
│   │   ├── temperatures
│   │   └── pressures
│   └── experiment_2
│       └── temperatures
└── metadata
    └── sensor_names

```

`experiments/experiments_1`, `experiments/experiments_2` and all are nodes or keys associated to their data, we can inspect all the keys from a file doing so:

```python

with pd.HDFStore("file.hdf5", mode="r") as store:
    print(store.keys())

```

Because its binary I will show you by exporting from lisible data.

```python

import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["Paris", "London", "New York"]
})

df.to_hdf("file.hdf5", 
          key="people", 
          mode="w",
          format="fixed",
          complib="zlib",
          complevel=3)

```

Here I exported in `HDF5` format with `"fixed"` flavor.

We could have created a deeper key such as `"datasets/people"` even if `"datasets"` was not initially created.

Contrary to `"table"`, it's less complex ->  quicker read and write.

But with this format, you can't do partial reads (start - end), append or query on the fly for reading querried rows into memory.

Also, note that I used `"w"` mode, meaning that it erased all possible other keys in the `HDF5` file.

As written before, `key` is like a table name.

If I'd use `a`, it would have created a new table in the file.

As seen before, a single file can store multiple tables / keys.

The differences between `"fixed"` and `"table"` format can be summarized here:

| Feature | `fixed` | `table` |
|---|---|---|
| Read the entire DataFrame | Yes | Yes |
| Read selected rows with `where=` | No | Yes |
| Append new rows | No | Yes |
| Usually faster for full read/write | Yes | No |
| Supports indexed/query columns | No | Yes |
| Internal representation | Serialized pandas object | PyTables table |

`"fixed"` and `"table"` are best understood as:

A `pandas` serialization format built on top of `HDF5`, **not a universal cross-language tabular format**.

`"table"` stores the DataFrame in a more structured, row-oriented `PyTables` table layout, with extra metadata and indexing informations that allow pandas to:

- append rows;
- select subsets with `where=`;
- index chosen columns for faster queries.

`PyTables` is a Python library for working with HDF5 files. 

It implements the serialization of dataframes in this file format for example.

We can extract data from an `HDF5` file with just `PyTables`:

```python

import tables

class Person(tables.IsDescription):
    name = tables.StringCol(20)
    age = tables.Int32Col()
    city = tables.StringCol(20)

with tables.open_file("people.hdf5", mode="w") as file:
    table = file.create_table("/", "people", Person)

    row = table.row
    row["name"] = "Alice"
    row["age"] = 25
    row["city"] = "Paris"
    row.append()

    table.flush()

```

They use fundamentally different storage layouts:

```

fixed
    DataFrame -> index arrays + column arrays + dtype blocks + metadata

table
    DataFrame -> PyTables table records + metadata + optional indexes

```

This is the `PyTables` machinery that allow to make a query while ingesting data to construct a `pd.DataFrame` for example.

But you tell me: "Is that just some overcomplicated machinery because at this point it still needs to scan columns before in order to evaluate the query for returing the matching rows ?"

And here is the subtelty.

In a lot of simple queries we just need to scan one or not much columns, think of `where age > 20`.

In fact it just needs to scan the `age` column, then get the matching indices, and finally scan the other columns at those indices.

Also, when appending on to a datafrae that is serialized under the "table" format, it obviously doe not:

```

old_table_bytes + new_rows + trailing_metadata

```

with everything after the insertion point shifted and rewritten.

Instead, think more like:

```

table
├── chunk 0 # rows 0-999
├── chunk 1 # rows 1000-1999
├── chunk 2 # rows 2000-2999
└── chunk 3   # newly allocated when appending

```

With the chunks not being contiguous on disk.

When we do:

```python

df_new.to_hdf(
    "file.h5",
    key="people",
    format="table",
    append=True,
)

```

`PyTables` roughly does this:

Extends the logical row count of the table.
Writes the new records into available space in the last chunk.
Allocates additional chunks if necessary.
Updates HDF5/PyTables metadata and indexes.

So conceptually:

- fixed

1. pandas-specific HDF5 encoding
2. optimized for saving/loading the whole object

- table
    
1. pandas-specific HDF5 encoding
2. organized as a `PyTables` table
3. includes schema/query metadata
4. optionally includes indexes on data columns

Also, you can have both format in a single-file, conceptually:

```

/
├── people          # fixed-format pandas serialization
│   ├── axis0
│   ├── axis1
│   ├── block0_items
│   └── block0_values
└── orders          # table-format pandas serialization
    └── table

```

Because `format` cntrols how the dataframe is serialized under its key, not the serialization of all dataframes in the whole file.

Note that in `HDF5`, compression is optional but as you see in the API, we can tell the engine to compress with and we can choose compression level.

Available compression libs:

- "zlib" -> standard, safe
- "blosc" -> fast (often best)
- "bzip2" -> strong but slow
- "lzo" -> very fast (less common)

`complevel` is between 0 (weakest, fastest) and 9 (strongest, slowest)

Then we do the following to read it.

```python

df = pd.read_hdf("file.hdf5", key="people")

print(df)

```

Output.

```
      name  age      city
0    Alice   25     Paris
1      Bob   30    London
2  Charlie   35  New York

```

The compression is the same as the format, only key dependent.

For a dataset, the compression engine and level is chosen when it is created.

Therefore, chinks of a dataset in the "table" format for example have the exact same compression identity.

#### `table` flavor

```python

import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["Paris", "London", "New York"]
})

df.to_hdf("file2.hdf5", 
          key="people", 
          format="table",
          data_columns=["age"],
          complib="zlib",
          complevel=3)
```

Here, we have to choose the columns that will have some metadata ready for querying on the fly while ingesting with `data_columns=[...]`, like so.

```python

df = pd.read_hdf("file2.hdf5", 
                 key="people", 
                 where="age > 30") # neat !
print(df)

```

Output.

```

      name  age      city
2  Charlie   35  New York

```

Here, an example of a patial read.

```python

df = pd.read_hdf("file2.hdf5", 
                 key="people", 
                 start=0, 
                 stop=2)
print(df)

```

Output.

```

    name  age    city
0  Alice   25   Paris
1    Bob   30  London

```

And here, we can append data to `HDF` file.

```python

import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["Paris", "London", "New York"]
})

df.to_hdf("file2.hdf5", 
          key="people", 
          format="table",
          data_columns=["age"],
          complib="zlib",
          complevel=3,
          append=True)

df = pd.read_hdf("file2.hdf5", key="people")
print(df)

```

Output.

```
      name  age      city
0    Alice   25     Paris
1      Bob   30    London
2  Charlie   35  New York
0    Alice   25     Paris
1      Bob   30    London
2  Charlie   35  New York

```

## Going back to plot

We can do it the "classical" way:

```python

```












