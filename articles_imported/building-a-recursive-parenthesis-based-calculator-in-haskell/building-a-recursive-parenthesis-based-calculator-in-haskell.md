## Context

In this project, we build a **complete calculator** in Haskell that can evaluate normal
arithmetic expressions written in _parenthesis notation_ (e.g. `(3+5)*(2-(4/2))`).
This goes far beyond Reverse Polish Notation: we now need to handle nested parentheses, operator precedence,
and negative values — all from scratch.


The goal of this project isn’t just to make a calculator, but to explore:


- Recursive parsing
- Pattern matching and list handling
- Working with indices and substrings in a pure functional way
- Implementing operator precedence manually

## 1\. The overall structure

The calculator works in three major steps:


1. **Tokenization of parentheses** — finding pairs of `( ... )` and nesting depth.
2. **Recursive substitution** — evaluating innermost subexpressions first.
3. **Direct computation** — once parentheses are gone, handling `* /` before `+ -`.

```haskell


calc :: [Char] -> [Char]
calc xs =
    let (ids, nums) = parserPar xs
        newxs = subCalc xs ids nums
    in protoCalc newxs

```

## 2\. Parsing parentheses

The first big challenge is identifying where parentheses start and stop — including nested ones.
That’s the job of `parserPar` and `subParserPar`.


```haskell


parserPar :: [Char] -> ([Int], [Int])
parserPar xs = subParserPar xs [] [] [] 0 0

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

Each time we find an opening parenthesis `(`, we push a new nesting level.
Each closing parenthesis `)` maps back to its matching `(` by looking for the most recent depth.
The result is two lists:


- `ids` — character positions of parentheses
- `nums` — nesting levels

The helper `findFirstZero` finds the position of a closing match from the end.


## 3\. Evaluating nested parentheses recursively

Now that we know which parentheses belong together, we can evaluate the most nested pair first.
The function `subCalc` does this recursively:


```haskell


subCalc :: [Char] -> [Int] -> [Int] -> [Char]
subCalc xs [] [] = xs
subCalc xs ids nums =
    let curmax = myMax nums
        [id1, id2] = grepn2 curmax nums
        idstrt = (ids !! id2)
        idstop = (ids !! id1)
        xsstrt = if idstrt > 0 then getRangeList xs [0..(idstrt - 1)] else []
        xsstop = if idstop + 1 < length xs then getRangeList xs [(idstop + 1)..(length xs - 1)] else []
        xsbetween = getRangeList xs [(idstrt + 1)..(idstop - 1)]
        rslt = protoCalc xsbetween
        newxs = if head rslt /= '-'
                then xsstrt ++ rslt ++ xsstop
                else (getRangeList xsstrt [0..(length xsstrt) - 2]) ++ rslt ++ xsstop
        (newids, newnums) = parserPar newxs
    in subCalc newxs newids newnums

```

In plain English:


1. Find the _deepest_ pair of parentheses (highest nesting value).
2. Extract the substring inside that pair.
3. Compute it with `protoCalc`.
4. Replace it with its result inside the main expression.
5. Re-parse the string (since parentheses may have changed) and repeat recursively.

Eventually, there are no more parentheses — then we fall back to `protoCalc`.


## 4\. Computing plain arithmetic expressions

`protoCalc` handles expressions with just numbers and `+ - * /`.
It gives precedence to multiplication and division by calling `subProtoCalc` first,
then addition and subtraction through `subProtoCalc2`.


```haskell


protoCalc :: [Char] -> [Char]
protoCalc xs =
    let outxs = subProtoCalc2 (subProtoCalc xs []) [] 0
    in outxs

```

### Multiplication and Division

`subProtoCalc` recursively scans through `*` and `/`, replacing them with computed results.
It even supports negative numbers by checking if the next character is `'-'`.


```haskell


subProtoCalc (x:xs) outxs
    | x == '*' = ...
    | x == '/' = ...
    | otherwise = subProtoCalc xs (outxs ++ [x])

```

### Addition and Subtraction

`subProtoCalc2` then handles `+` and `-` in a similar recursive pass:


```haskell


  subProtoCalc2 (x:xs) outxs n
    | x == '+' = ...
    | x == '-' = ...
    | otherwise = subProtoCalc2 xs (outxs ++ [x]) (n + 1)

```

This two-phase evaluation emulates operator precedence manually, entirely with string recursion and pattern matching.


## 5\. Tokenization, recursion, and purity

The most fascinating part of this calculator is that everything is done without mutable state:
no variables, no loops — just recursion and pure string transformations.


- **Tokenization** — achieved through recursive parsing of parentheses.
- **Recursion** — drives both the parsing and arithmetic computation.
- **Purity** — every transformation returns a new string instead of mutating the old one.

Although it’s not the most efficient possible design, it’s a beautiful demonstration of how
functional programming can model complex processes like parsing and evaluating arithmetic — purely through recursion and pattern matching.


## 6\. Wrap-up

This “parenthesis-based” calculator project is a deep dive into recursive problem-solving in Haskell.
We learned to:


- Parse and track nested parentheses manually
- Recursively evaluate the deepest expressions first
- Build our own operator precedence logic
- Write pure functions that progressively transform strings

Together with the earlier projects (like the RPN and comprehension-based examples), this one shows just how expressive Haskell can be —
you’re not telling the computer _how_ to compute step by step, but describing _what_ the relationships between parts of the expression are.