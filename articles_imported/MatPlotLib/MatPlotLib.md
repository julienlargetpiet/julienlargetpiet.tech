
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

First note, default index is just `[0, n-1]`.

Second note, you can also create a `pd.Series` of chosen length that is filled with a special value.

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

Or truly borrowing the infamous `[X] * N` to create list of length `N`:

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
print(y3[1])
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
print(y3.iloc[1])
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

Now you guess what will happen with `.loc[3:5]` for example --> multiple `.loc[]` (`.loc[3]` + `.loc[4]`)

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

Also a quick note about the behavior of `.iloc[]`.

- `[A:B]` -> returns a view, but when you modifie it, it silently copies it before doing the write (Copy On Write) (so it never modifies the origin)

- `[[B, A, ...]]` -> returns a copy

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

Quick note about the behavior of `.loc[]`.

It behave exacly like `.iloc` for this.

But when index is not sorted:

```python
import pandas as pd

s = pd.Series([10, 20, 30, 40], index=[10, 5, 2, 8])
```

Now try:

```python
s2 = s.loc[10:2]
```

What you expect

Something like:

**[10 -> 2] slice**

What actually happens

`.loc` slicing is label-based AND order-dependent.

Since the index is not sorted, pandas:

- does NOT interpret this as a clean slice
- cannot map it to a contiguous memory region
- falls back to more complex selection logic

->  Result:

- order follows the existing index order
- not guaranteed contiguous
- often involves a copy earlier than you expect

## `pd.Index()`

We just saw that index arte used in `pd.Series` to map value to an index.

Until now, we just have seen that indices are just list we put in the parameter `index`.

It's not that useful to know that, but in fact they have their own types.

```python3
x = pd.Index([0,1,2,3])
print(x)
```

Output.

```
Index([0, 1, 2, 3], dtype='int64')
```

And they act just like list, no `iloc` / `loc`, just normal random access.

Hmm, not totally.

They support vectorized operation.

```python
x = pd.Index(["julien", "antoine", "lucas", "baptiste"])
print(x.str.upper())
```

Output.

```
Index(['JULIEN', 'ANTOINE', 'LUCAS', 'BAPTISTE'], dtype='str')
```

Also, lookup are O(1).

```python
print(x.get_loc("antoine"))
```

Output.

```
1
```

Look if we have samekey multiple times, it returns a **boolean numpy array**. (that is one of the worst API ever lol, it's like if the engneer wanted to make the more unpredictable data engine ever)

```python
x = pd.Index(["julien", "antoine", "lucas", "baptiste", "antoine"])
print(x.get_loc("antoine"))
```

Output.

```
array([False,  True, False, False,  True])
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

### `pd.RangeIndex`

That's the one we implicitely worked with.

For example, default pandas dataframe comes with this one as their index.

It does not store index as a huge numpy array, but instead as a `Range(start, stop, step)`

Then, wen you define a Serie, use RangeIndex:

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

So when random accessing some data, it does something like that:

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

So if i have this array:

```python
print(ser)
```

Output.

```
0    1
1    2
2    1
3    1
4    2
5    3
Name: c1, dtype: int64
```

Its values are numpy array, we get via:

```python
print(ser._values)
```

Output.

```
array([1, 2, 1, 1, 2, 3])
```

Then you are able to understand this:

```python
label = 3

pos = ser.index.get_loc(label)   # label -> integer position
value = ser._values[pos]         # read actual data array at that position
```

You can apply slices on your `RangeIndex` object.

```python
print(ser.index[::-1])
```

Output.

```
RangeIndex(start=5, stop=-1, step=-1)
```

You can transform your `RangeIndex` object as an numpy array.

For that a trick is to use `.get_indexer()` method.

**For each label in target, where is that label located in this index?**"

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

So you we will make:

```python
ser.index.get_indexer(ser.index)
```

Output.

```
array([0, 1, 2, 3, 4, 5])
```

Here are some methods Index have:

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

Of course `RangeIndex` are only used when the Index is monotonicly increasing.

And also when the step is a constant integer.

You can check that by printing it out -> if `RangeIndex` then it is monotonicly increasing.

Or checking is value `is_monotonic_increasing`.

```python
>>> idx1 = pd.Index([2, 0, 1])
>>> idx1.is_monotonic_increasing
False
>>> idx1
Index([2, 0, 1], dtype='int64')
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

`ordered=True` has nothing to do with sort order:

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

If i set `ordered=False`, i can not even do comparison to a category that belongs to the set of possible categories.

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

Because we are in `CategoricalIndex`, you can check if an element belongs to the set of categories.

```python
>>> "B" in x.index
True
```

Loc, output differe when it comes to dupplication:

```python
>>> x.index.get_loc("B")
2
>>> x.index.get_loc("A")
array([ True,  True, False,  True])
```

More predicatble is:

```python
>>> x.index=="B"
array([False, False,  True, False])
```

Is In ?

```python
>>> x.index.isin(["A", "B"])
array([ True,  True,  True,  True])
```

The codes, map each element to the index of the category.

```python
>>> x.index.codes
array([0, 0, 1, 0], dtype=int8)
```

All elemnts are "A" apart fom the thirs one which is `x.index.values[1]` = "B"

Description of index:

```python
>>> x.index.values
['A', 'A', 'B', 'A']
Categories (3, str): ['A' < 'B' < 'C']
```

Taking / deleting / inserting

Because it is an Index:

```python
idx.take([0, 2])
idx.delete(1)
idx.insert(0, "large")
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

```
"A" first occurrence  -> False
"A" seen again        -> True
"B" first occurrence  -> False
"B" seen again  -> True
"C" unused category   -> no output at all
```

7. Taking / deleting / inserting

Because it is an Index:

```python
idx.take([0, 2])
idx.delete(1)
idx.insert(0, "D")
```

But insertion must respect categories:

```python
idx.insert(0, "D")
```

will fail unless "D" is already a category.

Replace category under conditions mask.

```python
>>> x.index.where(x.index != "A", other="C")
CategoricalIndex(['C', 'C', 'B', 'C'], categories=['A', 'B', 'C'], ordered=True, dtype='category')
```

Or you can extend conditions to any boolean list.

```python
>>> x.index.where([True, False] * 2, other="C")
CategoricalIndex(['A', 'C', 'B', 'C'], categories=['A', 'B', 'C'], ordered=True, dtype='category')
```

Export to numpy. (of course, we can do that with other Index Type)

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

To rename category, you can apply a mapping with `.map({...})` method.

Note that all category that re present in the actual data must be present in the dict, or it will result in Nan values for those not rpesent.

```pyton
>>> x.index.map({"A": "a", "B": "b", "C": "c"})
CategoricalIndex(['a', 'a', 'b', 'a'], categories=['a', 'b', 'c'], ordered=True, dtype='category', name='size')
```

Here, because "C" is not present it will be converted to a raw `pd.Index` -> not what you want.

```python
>>> x.index.map({"A": "a", "B": "b"})
Index(['a', 'a', 'b', 'a'], dtype='str', name='size')
```

And even worse if none of the category present in actual data are present in the dict.

```python
>>> x.index.map({"C": "c"})
Index([nan, nan, nan, nan], dtype='str', name='size')
```

You can of course map the category to number and it would return a `CategoricalIndex`, BUT if there are too much category it mght fail to map to a `CategoricalIndex` and therefore to a plain `Index`, so be careful with numbers and use string instead.

```python
>>> x.index.map({"A": 1, "B": 2, "C": 3})
CategoricalIndex([1, 1, 2, 1], categories=[1, 2, 3], ordered=True, dtype='category', name='size')
```

Also not that collapsing category lead to a plain `Index`.

```python
>>> x.index.map({"A": "a", "B": "c", "C": "c"})
Index(['a', 'a', 'c', 'a'], dtype='str', name='size')
```

Then yess, i found that to be a very weird behavior, because that is the contrary to the previous problem where category makes more sense to be, but here it is.

If you want to make it a categorical index, just convert it back to one.

```python
>>> pd.CategoricalIndex(x.index.map({"A": "a", "B": "c", "C": "c"}), 
                                    name=x.index.name, 
                                    ordered=x.index.ordered
)
CategoricalIndex(['a', 'a', 'c', 'a'], categories=['a', 'c'], ordered=True, dtype='category', name='size')
```

(Set of categories are computed from actual category in data)

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
>>> x.index.rename_categories(["a", "b", "c"])
CategoricalIndex(['a', 'a', 'b', 'a'], categories=['a', 'b', 'c'], ordered=True, dtype='category', name='size')
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
>>> x.index.map(lambda x: np.random.choice(["A", "B", "C", "D", "E", "F", "G"]))
```

Because we think it applies one per row.

But now in fact it apply **per category**, then always between 1 and n (already existing categories) here.

Output.

```python
Index(['C', 'C', 'E', 'C'], dtype='str', name='size')
```

So what if we try to add a chaos factor, like `time.time()` ?

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

Same thing, it **stores result per category**.

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

Others `pd.MultiIndex` constructor are:

```python
pd.MultiIndex.from_arrays(
    [["A", "A", "B", "B"], [1, 2, 1, 2]],
    names=["group", "number"],
)
```

Or cleaner (built in cartesian product):

```python
pd.MultiIndex.from_product(
    [["A", "B"], [1, 2]],
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

`FrozenList` is a special pandas datatype that stipulates a list that should not be modified.

I also, can have the index list for each level, that stores the index of a group in a level for a row:

```python
>>> x.index.codes
FrozenList([[0, 0, 1, 1], [0, 1, 0, 1]])
```

Note, that is not boolean mask at all, just lists that for each level, stores the corresponding group as its index in the corresponding level.

To get the names of the levels do:

```python
>>> x.index.names
FrozenList(['group', 'number'])
```

Rename them:

```python
x.index = x.index.set_names(["Group", "Number"])
```

Or on the Series/DataFrame directly:

```python
x = x.rename_axis(["Group", "Number"])
```

Now you have `groupby()` for free !

And please don't do that for filtering even tho it's correct:

```python
>>> x[(x.index.codes[0] == 1) & (x.index.codes[1] == 0)]
Group  Number
B      1         2
dtype: int64
```

You can just simply do:

```python
>>> x.loc[("B", 1)]
np.int64(2)
```

Here, it just returns a numpy int64 because just one match.

But if you want predictable return type do:

```python
>>> x.loc[[("B", 1)]]
Group  Number
B      1         2
dtype: int64
```

Always a `pd.Series`.

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

With `MultiIndex`, you aso have `.xs()` method that does the same job but maybe more intuitively.

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

Personnaly i think that is one of the worst and most unpredictable API design ever done, because until you select all levels, `drop_level` has an effect, but once the filters are done over all levels, it has no longer any effect.

```python
>>> x.xs(("B", ), level=["Group"], drop_level=True)
Number
1    2
2    3
dtype: int64
>>> x.xs(("B", ), level=["Group"], drop_level=False)
Group  Number
B      1         2
       2         3
dtype: int64
```

And now, it just acts as `True`.

```python
>>> x.xs(("B", 1), level=["Group", "Number"], drop_level=True)
Group  Number
B      1         2
dtype: int64
>>> x.xs(("B", 1), level=["Group", "Number"], drop_level=False)
Group  Number
B      1         2
dtype: int64
```

Even tho by default it is `False`.

```python
>>> x.xs(("B", ))
Number
1    2
2    3
dtype: int64
```

Then we get that whenever it can output the result as a scalar, it does it.

```python
>>> x.xs(("B", 1))
np.int64(2)
```

Even when you precise to not drop levels, weird but ok...

```python
>>> x.xs(("B", 1), drop_level=False)
np.int64(2)
```

So in `.xs()` API, the only thing that assure you to get a `pd.Series` is putting something in `level` parameter, LOL.

Use `.loc`, or get rid of pandas at this point.

In addition to all basic Index methods, it also have `.map()` method.

```python
idx = pd.MultiIndex.from_tuples(
    [("A", 1), ("A", 2), ("B", 1), ("B", 2)],
    names=["group", "num"],
)

idx.map(lambda x: f"{x[0]}-{x[1]}")
```

Output.

```
MultiIndex([('A', 1),
            ('A', 2),
            ('B', 1),
            ('B', 2)],
           names=['group', 'num'])
```

Of course it comes with all inder, remove, unique... basics methods and also set methods.

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

For time unit between hour and less, `pd.DateOffset()` and `pd.Timedelta()` are the same, because that are fixed time unit.

But as we begin to speak about day, by how many hours it is made of, 24 hours ? Yesss, but sometimes in the year it is 23 hours or 25 hours.

So at this moment it starts to differe.

Btw, `Timedelta` does not even have `months` or `years`.

Then use `pd.Timedelta(time_unit)` when yo want to ADD a certain amount of time unit.

And use `pd.DateOffset(time_nit)` when you want "the same date of origin + an offset of the unit time but **aware of calendar - interpreted by the calendar accoding to the local TimeZone**"

So after saying this you know that those are equivalent.

```python
>>> pd.Timestamp("2024-01-01 11:10:00") + pd.Timedelta(minutes=1, hours=2)
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

You can also associate an ingeter to jump n unit of time.

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

Now, concept of Buisnes, Month Start "MS" and Month End "ME".

"MS" is the next date of a beginning of a month.

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

Same for "ME".

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

Those are possible because internaly it mst use timezone calendar aware (`pd.DateOffset(...)` ...).

Same concept for "YS" and "YE".

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

Note that "W" is basically a shortcut for "w-SUN".

You can have by Tuesday for example, with "W-TUE.

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

Of course it has all basic Index methods pus a bunch of specific date methods.

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

No, `is_week_start` or `is_week_end`, then use `day_of_week` index logic (0 - 6) (Monday - Sunday).

To get the step of time unit a `DatetimeIndex` is built with.

```python
>>> x.freq
<Week: weekday=1>
```

Or in string:

```python
>>> x.freqstr
'W-TUE'
```

But, this only is set to this value because we constructed the `DatetimeIndex` with `date_range()` constructor superset that puts a value to te frequency.

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

You can also convert to an numpy array of python standard datetime.

```python
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

Btw, here an explanaton on differences between `datetime.date` and `pd.Timestamp`.

They represent similar things, but Timestamp is built to fit pandas/NumPy time-series machinery.

Basic difference

```python
from datetime import datetime
import pandas as pd

dt = datetime(2024, 1, 16, 12, 30)
ts = pd.Timestamp("2024-01-16 12:30")
```

Types:

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

Python datetime.datetime supports microseconds:

```
2024-01-16 12:30:00.123456
```

Pandas Timestamp supports finer precision, usually nanoseconds:

```python
>>> pd.Timestamp("2024-01-16 12:30:00.123456789")
Timestamp('2024-01-16 12:30:00.123456789')
```

Python datetime cannot represent the last 789 nanoseconds directly.

Missing values

Pandas has a datetime missing value:

```
pd.NaT
```

-> Not a Time

Example:

```python
>>> pd.to_datetime(["2024-01-01", None])
DatetimeIndex(['2024-01-01', 'NaT'], dtype='datetime64[ns]', freq=None)
```

Python datetime has no native datetime-specific NaT; you usually use None.

Vectorization

Python datetime is a scalar object. If you have many of them in a list, operations are Python-loop-ish:

```python
dates = [datetime(2024, 1, 1), datetime(2024, 1, 2)]
```

Pandas uses Timestamp scalars plus DatetimeIndex / Series[datetime64] arrays:

```python
idx = pd.date_range("2024-01-01", periods=3, freq="D")

idx.year
idx.month
idx + pd.Timedelta(days=1)
```

Those are vectorized pandas operations.

Timezone handling

Both can be timezone-aware, but pandas integrates it into DatetimeIndex:

```python
>>> ts = pd.Timestamp("2024-03-31 12:00", tz="Europe/Paris")

>>> ts.tz_convert("UTC")
Timestamp('2024-03-31 10:00:00+0000', tz='UTC')
```

With Python datetime, timezone handling exists, but it is lower-level:

```python
from datetime import timezone, datetime

dt = datetime(2024, 3, 31, 12, 0, tzinfo=timezone.utc)
```

Note that creating a datetime that when you create a `datetime.datetime`, you have to precise year, month and day, other are set to default `0` value.

Pandas gives you `.tz_localize(...), .tz_convert(...)`, DST handling parameters, and vectorized timezone operations.

Date arithmetic

Python:

```python
from datetime import timedelta

dt + timedelta(days=1)
```

Pandas:

```python
ts + pd.Timedelta(days=1)
ts + pd.DateOffset(months=1)
```

The important pandas-specific part is `DateOffset`:

```python
>>> pd.Timestamp("2024-01-31") + pd.DateOffset(months=1)
Timestamp('2024-02-29 00:00:00')
```

Python’s `timedelta` has no “months” because months are not fixed durations.

Range / limits

Pandas timestamps backed by NumPy-style nanosecond datetimes have a limited range, roughly years 1677 to 2262 for nanosecond precision.

Python datetime supports years 1 to 9999.

So this works in Python:

```python
datetime(3000, 1, 1)
```

but may not fit into pandas’ nanosecond datetime dtype cleanly.

Conversion

Python datetime to pandas timestamp:

```python
ts = pd.Timestamp(datetime(2024, 1, 16, 12, 30))
```

Pandas timestamp to Python datetime:

```python
dt = ts.to_pydatetime()
```

Date-only Python object:

```python
>>> ts.date()
datetime.date(2024, 1, 16)
```

-> Loss of precision here

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

Note, here seconds and lower are not printed out because i got 0 of them, but are still taken in count.

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

- Python scalar date+time object
- general-purpose
- microsecond precision
- huge year range
- no vectorized array behavior

**pd.Timestamp**

- pandas scalar date+time object
- integrates with DatetimeIndex / Series
- nanosecond-oriented
- supports pd.NaT ecosystem
- strong timezone/time-series integration
- works with Timedelta and DateOffset

In pandas work, stay with Timestamp, DatetimeIndex, and datetime64 as long as possible. Convert to Python datetime mostly for interoperability with libraries that expect standard Python objects.

Final Cheat Sheet:

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
idx.tz
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

## Would you mind take some DataFrame ?

You can create a DataFrame in multiple ways.

### First, by reading a `CSV`.

```python
df = pd.read_csv("example.csv",
                 sep=",",
                 encoding="latin1")
```

For a better control of columns types, which led to a **faster ingestion process** (because no inference), you can choos column types direclty.

But for dates are something special, you can not tell that a colun is a `datetime[us]` type directly in parsing.

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

Yess, but they introduced a specific option for that caled `parse_dates`.

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

And after let add your specific parsing logic inside the `pd.to_datetime()` function.

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

So if yo want to store just its unit time you signed up for ;) store them as `datetime` object.

```python
df["date2"] = pd.to_datetime(df["date2"], format="%H:%M:%S").dt.time
print(df.dtypes)
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
```

And you still can manipulate `date2` values as proper datetime.

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

`datetime64[us]` as its name suggest is encodedwith only 64 bits.

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

Ouch it works, but header are takein in count as the third line lol, which is from the ENGINE POV, understable (even if i expected smarter behavior).

To remedy to this problem, we simply declare the `skiprows` as a range from 1 to 2.

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

Because what is skiprows ?

It just tell which row indices to skip.

And also `skiprows=2` is equivalent to `range(0, 2)`.

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

### Generic Table (twin of `pd.read_csv()`)

```python
df = pd.read_csv("example.csv",
                 sep=",",
                 encoding="latin1")
```

The only change is the default value of `sep` which is set to a **tabulation** `\t`.

You can also specify from which line yo begin to read with `header=2` for example -> here the header is the **second** line and the data will begin at the fourth row..

You can also specify the columns you want to read with `usecols`.

#### Partial reads (Columns)

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

You also note that we do not need any `quotechar` neither `excapechar`, because here you literally provide the scheme where a column have a **constant** width.

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


### `PARQUET` file.

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

I can retry it and now i have.

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

Now, i want to read it!

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

Btw, wat is the architecture of predicates in this argument ?

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

That's the definition of Disjunctive Normal Form.

#### Going back to partitions

What happen to the filestructure if i partition accross multiple columns ?

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

Does the filestructure output depends on th order of `partition_cols` ?

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

It is a group of row from which you can decide the size.

Each row groups exposes some metadata about their columns, like min, max...

Then when we use filters whie reading a `PARQUET` file, the engine will optimize its ingestion time by skipping unnecessary data.

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

It also do it file-wise, concerning the file partitions.

Then, if you know that your data pipeline will often do a certain type of query on some columns, be aware to well partition the data bu the queried columns.

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

Note that here, i created a column just for the file partition and query optimization (`PIB_bucket`).

So at ingestion time, the engine will skip entire files that are `PIB_bucket < 10` and it will skip entire `row_groups` inside the matching files.

--> You can also put `columns=["col1", "col2"]` or `columns=[5, 3, 5]` for example

--> `use_threads=True` (if a lot of data to write)

### `FEATHER` format.

Same as `PARQUET` but not compressed -> quicker for ingesting data.

For this one you'll need to install `pyarrow`.

```bash
pip install pyarrow
```

It is a binary file too (like `PARQUET`) so i can not show it but i can make an export of an actualy understable data.

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

--> You can also put `columns=["col1", "col2"]` or `columns=[5, 3, 5]` for example (like for `PARQUET`).

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

### You knwo what ?

`PARQUET` should not be able to have the monopole on file partitioning over data.

So let's reimplement this pat at another abstraction level.

First, ingestion time.

We define a function that recursively list files that respect a condition defined in a function `f_mask`.

```python
def list_files_rec2(dr: str, 
                    f_mask) -> list[str]:
    rtn_lst = []

    try:
        for name in os.listdir(dr):
            cur = os.path.join(dr, name)
            if os.path.isdir(cur) and not os.path.islink(cur):
                rtn_lst.extend(list_files_rec2(cur, f_mask))
            elif f_mask(cur):
                rtn_lst.append(cur)
    except PermissionError:
        pass
    return rtn_lst
```

We also need to define a mini-parser that will understand `filters` semantic:

```python
def f_satisfy(f: str, filters: list | None) -> bool:
    for cond in filters:
        ok = True
        for col, op, val in cond:  
            cur = get_var(f, col)
            if cur is None:
                ok = False
                break

            try:
                cur = float(cur)
            except:
                pass

            match op:
                case ">":   ok &= (cur > val)
                case ">=":  ok &= (cur >= val)
                case "=":   ok &= (cur == val)
                case "<=":  ok &= (cur <= val)
                case "<":   ok &= (cur < val)
                case _:     ok = False

            if not ok:
                break

        if ok:
            return True

    return False
```

That will be the the value of `f_mask`.

The we plug this together.

```python
def read_partitions(f: str,
                    *,
                    filters: list | None = [],
                    columns: list | None = None,
                    read_method) -> pd.DataFrame:

    filters = [] if filters is None else filters

    lst_files = list_files_rec2(f, lambda p: f_satisfy(p, filters))
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

Hmmm, but we can go further, preventing entering folders when we already know there won't be any file used.

For that we create `d_satisfy()` function.

```python
def d_satisfy(f: str, filters: list | None) -> bool:
    for cond in filters: 
        for col, op, val in cond:  
            ok = True
            cur = get_var(f, col)
            if cur is None:
                ok = False
                continue

            try:
                cur = float(cur)
            except:
                pass

            match op:
                case ">":   ok = (cur > val)
                case ">=":  ok = (cur >= val)
                case "=":   ok = (cur == val)
                case "<=":  ok = (cur <= val)
                case "<":   ok = (cur < val)
                case _:     ok = False

            if ok:
                break

        if ok:
            return True

    return False
```

And we plug that into `read_partitions()`.

```
def read_partitions(f: str,
                    *,
                    filters: list | None = [],
                    columns: list | None = None,
                    read_method) -> pd.DataFrame:

    filters = [] if filters is None else filters

    lst_files = list_files_rec2(f, 
                                lambda p: f_satisfy(p, filters),
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

So now a little bit of combinatorics (manualy because we al love algos).

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

That's just:

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

The `*` is weird, but it just mean unpacking a tupple to fit the args, look:

```python
def f(a, b):
    print(a, b, c)

f((2, 3, "DD"))
```

Output:

```
2 3 DD
```

But here we'll continue with original one.

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

In the first phase, we see the creation of `dct`, the dict passed to `make_predicates(...)` maping each col to all its unique values.

And you see ?

I recompute `lst_nb` because i need it too inside this function.

So yess, i could just pass it (by ref) to `make_predicates(...)` instead of allocating the same list inside `make_predicates(...)` but i wanted a good separation of concern even if it is justified to do it there...

Also i could have make `make_predicates` also returns a list of `ids` instead of recomputing them in the second phase, but again UNIX philosophie here.

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

Here it's generating al combinations, even for the ones that corresponds to zero rows.

If only we got an algorithm that could generate the combinations from actual data and not just from supposition of what data can be!

Have you heard about `grouping by X, Y, Z and ...`.

Yess, that's exactly the algorithm that we need here, and straight up from pandas.

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

Now here how we use all these funcs:

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

And ingestion is:

```
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

```

You see that `create_engine(...)` uses `psycopg2` connector.



#### MySQL - MariaDB

Instal binary:

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

### HDF5

### `fixed` flavor

Because its binary i will show you by exporting from lisible data.

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

Here i exported in `HDF5` format with `"fixed"` flavor.

Contrary to `"table"`, it's less complex (single binary blob) ->  quicker read and write.

But with this format, you can not do partial reads (start - end), append or query on the fly for reading querried rows into memory.

Also, note that i used `"w"` mode, meaning that it erased all possible other keys in the `HDF5` file.

`key` is like a table name.

If i'd use `a`, it would have created a new table in the file.

A single file can store multiple tables / keys.

`append=True` allow to add rows to an existing table, and as written before, is only supported with `format="table"`.

Note that in `HDF5` compression is optional, but as you see in the API, we can tell the engine tocompress it and we can choose compression level.

Available compression libs:

- "zlib" -> standard, safe
- "blosc" -> fast (often best)
- "bzip2" -> strong but slow
- "lzo" -> very fast (less common)

`complevel` is between 0 (weakest, fastest) and 9 (strongest, slowest)

Then we do that to read it.

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

### `table` flavor

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

Here, an example of patial read.

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

We can do it the "clasical" way:

```python

```












