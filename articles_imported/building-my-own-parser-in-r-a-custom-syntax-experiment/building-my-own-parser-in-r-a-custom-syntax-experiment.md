## Introduction

This was one of my older projects, a little bit eccentric but very educational. I wanted to see if I could design and implement a parser from scratch in R, complete with a brand-new syntax and functions to both read and write data. The project is part of my old data manipulation library written in R avaiable on this [repo](https://github.com/julienlargetpiet/edm1/blob/main/R/all_fun.R)

It wasn’t about reinventing JSON, XML, or YAML — it was about learning how parsing works at a low level, handling nested structures, and building a system that’s flexible enough to store and retrieve hierarchical data.

## The Custom Syntax

I invented a compact bracket-based format to represent hierarchical data. It looks like this:

```

(ok(ee:56))
(ok(oui(rr((rr2:6)(rr:5))))(oui(bb(rr2:1)))(ee1:4))
```

The rules are simple:

- Each node is wrapped in parentheses `(...)`.
- A node may contain a key-value pair (e.g., `ee:56`).
- A node may also contain nested nodes.
- Keys can repeat, creating multiple paths into the structure.

This makes it easy to represent trees, like nested directories or configurations.

## Reading Data: `read_edm_parser`

The function `read_edm_parser` lets you extract values from the dataset by providing a path vector.

```r

read_edm_parser(
  "(ok(ee:56))(ok(oui(rr((rr2:6)(rr:5))))(oui(bb(rr2:1)))(ee1:4))",
  to_find_v = c("ok", "oui", "rr", "rr2")
)
# [1] "6"

```

Here, the parser traverses the tree: `ok → oui → rr → rr2` and finds the value `6`.

If you ask for `c("ok", "ee")`, you get `56`.

This required writing from scratch:

- Parentheses matching with `pairs_findr`.
- Custom splitting with `better_split_any`, capable of handling nested symbols and regex quirks.
- Dynamic index conversion to map between character positions and parsed tokens.

## Writing Data: `write_edm_parser`

The companion function `write_edm_parser` allows adding new data into an existing parsed dataset.

```r

write_edm_parser(
  "(ok(ee:56))(ok(oui(rr((rr2:6)(rr:5))))(oui(bb(rr2:1)))(ee1:4))",
  to_write_v = c("ok", "oui"),
  write_data = c("ii", "olm")
)
# (ok(ee:56))(ok(oui(rr((rr2:6)(rr:5))))(ii:olm)(oui(bb(rr2:1)))(ee1:4))

```

This inserts a new node `(ii:olm)` under the path `ok → oui`. The dataset grows dynamically while keeping its hierarchical structure.

## Lessons Learned

- Parsing even a “toy” syntax is surprisingly hard — edge cases around parentheses, special characters, and multiple matches required a lot of custom logic.
- R is not the typical language for writing parsers, but it was a good test of string manipulation, recursion, and regular expressions.
- By building both read and write operations, I got a much deeper understanding of how real data formats like JSON or XML actually work under the hood.

## Conclusion

This was one of my older projects, but it shows how much you can learn by reinventing the wheel intentionally. By creating my own parser in R, I not only invented a mini data format but also trained myself in handling nested structures, indexes, and edge cases.

It’s not meant to replace JSON, but it was a great playground for anyone curious about how parsers work.