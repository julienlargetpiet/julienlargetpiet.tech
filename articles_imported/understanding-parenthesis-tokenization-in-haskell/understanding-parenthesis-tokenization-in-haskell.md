## Context

Before building a full arithmetic calculator in Haskell, there was one key challenge I needed to solve first:
**understanding and tokenizing parentheses.**

Parenthesis tokenization may sound like a small detail, but it’s actually a **necessary step** for
building my own calculator interpreter — the engine that later evaluates nested expressions like
`(3+(2*(5-1)))` correctly, respecting operator precedence and nesting depth.


## 1\. Why tokenization matters

In an arithmetic expression, parentheses determine the order in which subexpressions are evaluated.
To process them properly, a calculator must:


- Recognize where every `(` and `)` occurs
- Track how deeply nested each one is
- Know which pairs of parentheses match together

Once we have this information, we can safely evaluate the _innermost_ expressions first and work our way out — exactly
how human math logic works.


## 2\. The main entry point

To start, we define `parserPar`, a simple wrapper that calls the recursive worker function.
It returns two lists:


- `ids` — positions of each parenthesis
- `nums` — the nesting depth at that position

```haskell


parserPar :: [Char] -> ([Int], [Int])
parserPar xs = subParserPar xs [] [] [] 0 0


```

This setup initializes everything: the list of indices, the nesting counters, and starts recursion with both
index counters ( `n` and `n2`) at zero.


## 3\. The recursive core: `subParserPar`

Here’s the heart of the tokenizer — the recursive system that traverses the expression and records every
parenthesis and its depth:


```haskell


subParserPar :: [Char] -> [Int] -> [Int] -> [Int] -> Int -> Int -> ([Int], [Int])
subParserPar [] ids nums _ _ _ = (ids, nums)
subParserPar (x:xs) ids nums valxs n n2
    | x == '(' =
        let newids = ids ++ [n]
            newnums = nums ++ [n2]
            newvalxs = map (+1) valxs
            newvalxs2 = newvalxs ++ [1]
        in subParserPar xs newids newnums newvalxs2 (n + 1) (n2 + 1)
    | x == ')' =
        let newvalxs = map (\x -> x - 1) valxs
            idx = findFirstZero (reverse newvalxs) 0
            idx2 = (length valxs) - idx - 1
            newids = ids ++ [n]
            newnums = nums ++ [(nums !! idx2)]
        in subParserPar xs newids newnums (newvalxs ++ [0]) (n + 1) n2
    | otherwise = subParserPar xs ids nums valxs (n + 1) n2


```

Let’s decode what happens step by step:


- **`n`** — current character index in the string.
- **`n2`** — tracks how many nested levels we’ve entered so far.
- **`valxs`** — a stack-like list representing active parentheses’ depth states.

Whenever we hit:


- **An opening parenthesis** `(` —
   we add its index to `ids`, record the current depth in `nums`, and
   increment all ongoing nesting levels.

- **A closing parenthesis** `)` —
   we decrement nesting levels, find the matching opening index using `findFirstZero`,
   and store the corresponding depth.


This creates a perfect “map” of how parentheses are nested throughout the expression.


## 4\. Matching parentheses with findFirstZero

The helper `findFirstZero` is tiny but crucial — it looks backward in the list of nesting levels to
locate which `(` matches a given `)`:


```haskell


findFirstZero :: [Int] -> Int -> Int
findFirstZero (xi:xsi) n
    | xi == 0 = n
    | otherwise = findFirstZero xsi (n + 1)


```

By scanning from the end of the nesting state, it identifies the first “zeroed” value — meaning the most recently
closed parenthesis — and returns its position. This gives us a clear mapping between opening and closing brackets.


## 5\. Why this system was essential for the calculator

Without this parenthesis tokenization system, the calculator interpreter couldn’t have existed.
It’s the foundation that allows nested subexpressions to be extracted and evaluated in the correct order.
Once I had `(ids, nums)`, I could:


- Identify the _deepest_ expression to evaluate first
- Replace it in the string with its computed result
- Re-parse and repeat until no parentheses remain

In short, this parser is the **brain** that makes the whole calculator interpreter work — a recursive
mechanism that gives structure and hierarchy to raw characters.


## 6\. What this teaches about Haskell

- **Recursion** replaces loops — the entire traversal is recursive and state-free.
- **Pattern matching** allows simple, readable branching for `(`, `)`, and other cases.
- **Purity** ensures no mutable state — every step returns new lists.

Writing this tokenizer was an essential milestone.
Once the parentheses could be correctly identified and paired, everything else — arithmetic evaluation, precedence,
and final interpretation — naturally built upon it.


**In short:** Parenthesis tokenization wasn’t just a side utility — it was the first real piece of the calculator’s interpreter logic.