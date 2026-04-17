There is a moment every engineer hits.

You're staring at a text file-logs, CSVs, metrics, something messy-and you think:

> "I just need to extract, filter, compute, group, maybe transform a few columns…"

You reach for Python. Maybe Rust. Maybe even spin up a dataframe.

And then someone types a one-liner with `awk`.

It runs instantly. It's readable. It's correct.

And you realize:

**AWK is not a tool. It's a streaming data engine disguised as a scripting language.**

This article is a deep dive—from first principles to advanced patterns—so you don't just use AWK, but start thinking in it.

---

## 1\. The Core Idea: Pattern → Action

At its heart, AWK is built around a deceptively simple idea:

```awk


pattern { action }


```

Which translates to:

> "For each line, if the pattern matches, run the action."

Example:

```awk


awk '/error/ { print }' logfile


```

- `/error/` → pattern
- `{ print }` → action
- default `print` → prints the whole line

If you omit:

- **pattern** → runs on every line
- **action** → defaults to `{ print $0 }`

---

## 2\. The Data Model: Records and Fields

AWK processes input line by line. Each line becomes:

- `$0` → full line
- `$1`, `$2`, ... → fields
- `NF` → number of fields
- `NR` → line number

Default separator = whitespace.

### Memory footprint

That it is why it is vastly used for **high performance** data fltering, because of its **streaming** model (line by line in memory).

Then memory consumption is predictable and memory footprint is extremely low.

The only variables that last are default global variables like `NR, NF, FILENAME` and use custom variables, like a `count, sum, mapcnt...` (we will see later).

**Changing separators:**

```awk


awk -F';' '{ print $1, $3 }' file.csv


```

or:

```awk


BEGIN { FS=";" }


```

---

## 3\. Thinking in Columns

AWK is fundamentally column-oriented.

```awk


awk '{ print $1, $NF }'


```

You are not parsing text—you are manipulating structured rows.

---

## 4\. Filtering: Where AWK Starts to Shine

```awk


awk -F';' '$3 > 80'


```

```awk


awk -F';' '$1 == "Dupont" && $2 ~ /Maur/'


```

Operators:

- `==`, `!=`, `>`, `<`
- `~` → regex match
- `!~` → negation

---

## 5\. Control Flow

AWK supports full control structures:

```awk


if ($3 > 85) {
    print "High"
} else if ($3 == 85) {
    print "Exact"
} else {
    print "Low"
}


```

But often, AWK lets you avoid `if` entirely:

```awk


$3 > 85  { print "High" }
$3 == 85 { print "Exact" }
$3 < 85  { print "Low" }


```

---

## 6\. BEGIN and END

Execution lifecycle:

```text


BEGIN → per-line processing → END


```

Example:

```awk


BEGIN { print "Start" }
{ print $1 }
END { print "Done" }


```

> **Important:** In `BEGIN`, no input has been read → `NF = 0`

---

## 7\. Aggregation: AWK's Secret Weapon

```awk


{ sum += $2 }
END { print sum }


```

Average:

```awk


{ sum += $2; count++ }
END { print sum/count }


```

---

## 8\. Associative Arrays (Hash Maps)

AWK has built-in hash maps:

```awk


{ count[$1]++ }

END {
    for (k in count)
        print k, count[k]
}


```

Grouping + aggregation:

```awk


{ sum[$1] += $2 }


```

This is essentially: **GROUP BY** in SQL.

---

## 9\. Functions

AWK supports functions:

```awk


function square(x) {
    return x * x
}


```

But here is the twist: **variables are global unless explicitly declared local.**

```awk


function f(x,    i) {
    for (i = 0; i < 10; i++)
        print i
}


```

The extra parameters ( `i`) are local variables.

---

## 10\. String Processing

AWK has a surprisingly rich standard library.

**Substitution:**

```awk


sub(/foo/, "bar")     # first occurrence
gsub(/foo/, "bar")    # all occurrences


```

**Split:**

```awk


split($1, arr, ",")


```

--\> Fills the array with each elements splitted

but we can also use it as:

```awk


n  = split($1, arr, ",")


```

where n is the number of elements created --> length of arr.

Btw, `arr` is passed by reference !

```awk


{
    n = split($1, arr, ",")
    print "count:", n
    for (i = 1; i <= n; i++)
        print arr[i]
}


```

If no separator provided, `FS` will be the one chosen.

**Substring:**

```awk


substr($1, 2, 3)


```

Just returns the substring --> No side-effect

**Case:**

```awk


toupper($1)
tolower($1)


```

**Match:**

```awk


match($1, /regex/)


```

With: `RSTART`, `RLENGTH` being the global variables that are set after this command.

---

## 11\. Numeric Functions

```awk


sqrt(x)
log(x)
exp(x)
sin(x)
cos(x)
rand()
srand()


```

> **Important:** Call `srand()` to initialize the RNG before calling `rand()`.

---

## 12\. Field Mutation: The Hidden Power

You can modify fields directly:

```awk


$1 = "Jeanne"


```

Add new fields:

```awk


$(NF+1) = toupper($1)


```

> This is crucial: you are not just printing data—you are **transforming the record**.

---

## 13\. Print vs printf

```awk


print $1, $2


```

vs:

```awk


printf "%.2f\n", $4


```

- `print` → simple
- `printf` → formatted (C-style)

---

## 14\. The Mental Shift

At this point, AWK stops being _"a text tool"_ and becomes _"a streaming computation engine"_.

---

## 15\. A Real Example: From Raw Data to Structured Output

Dataset:

```text


Dupont ; Maurice ;67 ;1.75
Durand ; Marcel ;85 ;1.73
Marie ; Brun ;85 ;1.79
Alice ; Bonin ;90 ;1.75
Paul ; Dubois ;75 ;1.6


```

Full AWK program:

```awk


function addpintimes(x, x2) {
    for (i = 0; i < x2; i++) { x += 3.1415 }
    return x
}

BEGIN {
    FS=";"
    print "Separator is: '", FS, "'"
}

$3==85 || $2 ~ "B[a-z]+" {
    if ($3 > 85 && $1 !~ /arie.+/) {
        sum+=$4
        count++
        mapcnt[$1]+=$3
        $(NF + 1)=toupper($1)
        print NR, $1, $2, $3, $4, "Low", $5
    } else if ($1 ~ /arie.+/) {
        sum+=$4
        count++
        sub(/Marie.*/, "Jeanne", $1)
        mapcnt[$1]+=$3
        $(NF + 1)=toupper($1)
        print NR, $1, $2, $3, $4, "High", $5
    } else if (NF != 4) {
        print "Wrong number of fields for:", FILENAME
    } else {
        sum+=$4
        count++
        mapcnt[$1]+=$3
        $(NF + 1)=toupper($1)
        print NR, $1, $2, $3, $4, "High -", $5
    }
}

END {
    print "####"
    print "total:", sum, "moyenne:", sum/count

    delete mapcnt["Jeanne"]

    for (k in mapcnt) {
        val = addpintimes(square(mapcnt[k]), 3)
        var += val
        print k, val, length(k)
    }

    srand()
    printf "%100f\n", var + rand() * 100
}


```

and then we run it as:

```text


$ awk -f script.awk peoples.csv


```

where `peoples.csv` is the Dataset:

output:

```text


Separator is: ' ; '
2 Durand   Marcel  85  1.73 High - DURAND
3 Jeanne  Brun  85  1.79 Low JEANNE
4 Alice   Bonin  90  1.75 High ALICE
####
total: 5.27 moyenne: 1.75667
Alice  8109.42 6
Durand  7234.42 7
15415.649179


```

### Only Hashmaps

- Note that AWK only provides hashmap, but we can treat hashmap as lists, just with key as unique values, like counters.

### As many Code-Blocks as you want

Also a point worth mentioning is the fact that we can write as much blocks as we want, for instance we can tracduct this one code-block:

```awk


$3==85 || $2 ~ "B[a-z]+" {
    if ($3 > 85 && $1 !~ /arie.+/) {
        sum+=$4
        count++
        mapcnt[$1]+=$3
        $(NF + 1)=toupper($1)
        print NR, $1, $2, $3, $4, "High", $5
    } else if ($1 ~ /arie.+/) {
        sum+=$4
        count++
        sub(/Marie.*/, "Jeanne", $1)
        mapcnt[$1]+=$3
        $(NF + 1)=toupper($1)
        print NR, $1, $2, $3, $4, "Low", $5
    } else if (NF != 4) {
        print "Wrong number of fields for:", FILENAME
    } else {
        sum+=$4
        count++
        mapcnt[$1]+=$3
        $(NF + 1)=toupper($1)
        print NR, $1, $2, $3, $4, "Low -", $5
    }
}



```

into these 4 (approximately):

```awk


($3==85 || $2 ~ "B[a-z]+") && NF != 4 {
    print "Wrong number of fields fot: ", FILENAME
}

($3==85 || $2 ~ "B[a-z]+") && $3 > 85 && $1 !~ /arie.+/  {
    sum+=$4
    count++
    mapcnt[$1]+=$3
    print NR, toupper($1), $2, $3, $4, "High"
}

($3==85 || $2 ~ "B[a-z]+") && $3 <= 85 && $1 ~ /arie.+/ {
    sum+=$4
    count++
    sub(/Marie.*/, "Jeanne", $1)
    mapcnt[$1]+=$3
    $(NF + 1)=toupper($1)
    print NR, toupper($1), $2, $3, $4, "Low - Marie"
}

($3==85 || $2 ~ "B[a-z]+") && $3 <= 85 && $1 !~ /arie.+/ {
    sum+=$4
    count++
    mapcnt[$1]+=$3
    print NR, toupper($1), $2, $3, $4, "Low"
}



```

Conditions must be excluding if we want that only one block to be chosen per line.

---

## 16\. What This Program Actually Does

This is not a script anymore. It is a **pipeline**:

**Step 1 — Filtering**

```awk


$3==85 || $2 ~ "B[a-z]+"


```

**Step 2 — Conditional transformation**

- rename "Marie" → "Jeanne"
- classify rows
- normalize names

**Step 3 — Aggregation**

```awk


mapcnt[$1] += $3


```

**Step 4 — Schema evolution**

```awk


$(NF+1) = toupper($1)


```

**Step 5 — Final computation**

```awk


val = addpintimes(square(mapcnt[k]), 3)


```

**Step 6 — Randomized output**

```awk


printf "%100f\n", var + rand() * 100


```

---

## 17\. Why This Is Powerful

This single AWK program:

- parses structured data
- filters rows
- transforms values
- builds aggregates
- computes derived metrics
- modifies schema dynamically
- outputs formatted results

**All in one streaming pass.**

---

## 18\. The Real Insight

AWK is not:

- just a CLI tool
- just a scripting language

It is: **a lazy, streaming, column-aware computation engine**.

---

## 19\. When to Use AWK

Use AWK when:

- data is line-oriented
- transformations are column-based
- performance matters
- you want zero setup

---

## 20\. Final Thought

Most people stop at:

```awk


awk '{ print $1 }'


```

But the real power begins when you realize:

> **AWK lets you design data pipelines directly in the shell.**

And once that clicks…

You stop thinking: _"How do I process this file?"_

And start thinking: _"What transformation pipeline do I want to express?"_

That's when AWK becomes not just useful—

**but elegant.**