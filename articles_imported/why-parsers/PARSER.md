A lot of text-processing tools can get surprisingly far without a real parser.

For simple patterns, tools like `sed`, `awk`, or small ad-hoc string transformations are often enough. You match a fragment, replace it, split on a delimiter, maybe scan left to right, and the job is done. For flat data, it's often the most direct and elegant solution.

But this approach starts to break down when the input has structure.

As soon as you have nesting, precedence, escaping rules, ambiguous symbols, or context-dependent meaning, the input should not be considered as just a string. It becomes a small language. At that point, continuing to manipulate characters directly means you are building a parser anyway, just an implicit, fragile, and usually inefficient one.

This article is about discovering that boundary.

We start with a calculator implemented (in Haskell) through direct string manipulation: finding parentheses, replacing subexpressions, normalizing operators, and repeatedly scanning the input. It works, and that is precisely why it is interesting. Then we move toward the cleaner architecture: tokenize the input, give names to the pieces, and evaluate the structure according to clear rules and the performance gain is just MASSIVE.

That shift is the real lesson: for simple text, string logic is enough. For structured input, Tokenizer and Parser are the right tool.

The `ghc` version we will use all along this article is:

```bash

❯ ghc --version
The Glorious Glasgow Haskell Compilation System, version 9.4.7

```

## Context

In this project, we build a **complete calculator** in Haskell that can evaluate normal
arithmetic expressions written in _parenthesis notation_ (e.g. `(3+5)*(2-(4/2))`) as string of course.
This goes far beyond Reverse Polish Notation: we now need to handle nested parentheses, operator precedence,
and negative values, all from scratch.

This is a programm i like to do when discovering a language because algorithmically speaking it ia not really eleguant, so here we test the elegantness of a language measured on how much we can condense code.

## Boring Fundamental functions

Here we got some fundamentals function haskell base does not provide so we reimplement it.

So, first random acess.

```haskell

getRangeList :: [a] -> [Int] -> [a]
getRangeList [] _ = []
getRangeList _ [] = []
getRangeList xs (idx:ids) = (xs !! idx):(getRangeList xs ids) 

```

So we got that for example.

```haskell

ghci> getRangeList [1, 2, 3] [2, 1]
[3,2]

```

Here, just the grep command -> all indices of elements in a data structure that matches a pattern

Of course elements must support equality check `Eq`.

```haskell

grepn2 :: (Eq a) => a -> [a] -> [Int]
grepn2 cmp xs = subGrepn2 xs cmp 0 []

subGrepn2 :: (Eq a) => [a] -> a -> Int -> [Int] -> [Int]
subGrepn2 [] _ _ nxs = nxs
subGrepn2 (x:xs) cmp n nxs
    | cmp == x  = subGrepn2 xs cmp (n + 1) (n:nxs)
    | otherwise = subGrepn2 xs cmp (n + 1) nxs

grepmn2 :: (Eq a) => [a] -> [a] -> [Int]
grepmn2 [] _ = []
grepmn2 (x2:xs2) xs = (grepn2 x2 xs) ++ (grepmn2 xs2 xs)


```

So we got that for example.

```haskell
ghci> grepn2 "A" ["A", "B", "A", "C", "A"]
[4,2,0]
```

The infamous max.

Then elements must be ordonable `Ord`.

```haskell

myMax :: (Ord a) => [a] -> a
myMax xs = subMyMax xs (head xs)

subMyMax :: (Ord a) => [a] -> a -> a
subMyMax [] cmp = cmp
subMyMax (x:xs) cmp = 
    let cmp2 = if cmp >= x
              then cmp
              else x
    in subMyMax xs cmp2

```

Then, we go that for example:

```haskell
ghci> myMax [2, 4, 6, 1, 0]
6
```

## Naive version

### Parenthesis tokenization

Now, te fun begins.

Basically we need a way to tokenize parenthesis, then find thei index in the string then compute the result for the operations insde the prioritary nested parenthesis, the reconstruct the base string with this new result --> replacing the parethesis and its content already computed by its result.

Until there is no more matching operation (`+, -, / *`) or and parenthesis.

First, we need a parenthesis tokenizer that will take a string and output a pair of 2 lists.

One will give the index of each parethesis `(` and `)` in the string.

And the second list will be the same length of the first list but will encode the pair information.

For example:

```
[0, 0, 1, 2, 2, 1]
```

Will descrobe the following structure:

```
(...)(...(...)...)
```

The number of pairs is then `length of the list / 2`.

So at first abstraction layr we just ge the entry point.

```haskell

parserPar :: [Char] -> ([Int], [Int])
parserPar xs = subParserPar xs [] [] [] 0 0

```

`xs` is the string.

But we also provide 3 empty lists an 2 integers, why is that ?


Because it calls `subParserPar` which does all the parsing work essentially.

```haskell

subParserPar :: [Char] -> [Int] -> [Int] -> [Int] -> Int -> Int
                -> ([Int], [Int])
subParserPar [] ids nums _ _ _ = (ids, nums)
subParserPar (x:xs) ids nums valxs n n2
    | x == '(' = 
        let newids = ids ++ [n]
            newnums = nums ++ [n2]
            newvalxs = map (\x -> x + 1) valxs
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

You may directly note that `n` is just the index of each parenthesis -> `idx`.

Always incrementing and just taken into account for the index list when either `'('` is discovered with the construction of `ids`:

```haskell

let newids = ids ++ [n]

```

Then inputed in the recursive call.

```haskell
subParserPar xs newids newnums newvalxs2 (n + 1) (n2 + 1)
```

And when the function matches the character `')'`.

```haskell

newids = ids ++ [n]

```

And them same logic cals it with newly constructed `ids`.

And by defaut it just increments it.

```haskell

otherwise = subParserPar xs ids nums valxs (n + 1) n2

```

Now the list that encodes pair -> `nums`.

Ok this one changes when we encounter an opening parenthesis.

```haskell

newnums = nums ++ [n2]

```

It just appends `n2`, `n2` only increments when a new opening parenthesis is found, so like that a new pair is a new opening parenthesis.

```haskell

in subParserPar xs newids newnums newvalxs2 (n + 1) (n2 + 1)

```

But now the real work !

How to decide which pair is what ?

I mean we have to get a third (hidden) data structure / list that maintain all the logic, that's why we passed 3 lists and not only 2 to `subParserPar`.

```haskell

parserPar xs = subParserPar xs [] [] [] 0 0

```

Yess, its name is `valxs`.

The logic to find parenthesis pais is the following.

When an **opening parenthesis** is found, just append 1 to the list.

If there were already opening OR ending parenthesis discovered, then just increments them by `1`.

So here we distinguish the deph level by always incrementing one to those alredy discovered -> We maintain order.

But, when we discover an **ending parenthesis**, then semantically speaking it must be attached to an opening parenthesis.

So we just substract `1` to all discovered parenthesis and the most recent one where the result is equal to `0` is the opening parenthesis it pairs to. (**if the structure is correct which is the assumption for the function**)

That is the steps.

```haskell

let newvalxs = map (\x -> x - 1) valxs 

```

So here because we blindly mapped the substraction by `1`, we must match `0`, meaning get the index of the first `0` in the data structure.

In fact that's more lie a reverse match, because we need to get the index of last `0`.

That's why we got:

```haskell

idx = findFirstZero (reverse newvalxs) 0

```

`idx` is the index indexed on the reverse list so we must take the symmetric one.

```haskell

idx2 = (length valxs) - idx - 1

```

`findFirstZero` is just a simple `match` with `0` as the matching pattern.

```haskell

findFirstZero :: [Int] -> Int -> Int
findFirstZero (xi:xsi) n
              | xi == 0 = n
              | otherwise = findFirstZero xsi (n + 1)

```

That's all for the tokenization.


### Proto computation

First, not even talking about parenthesis, we got to handle PEMDAS, that' just the prioritary operators.

- P -> Parenthesis, already handled

- E -> expoent

- M -> multiplication

- D -> division

- A -> addition

- S -> substraction

Also here we will do convertions from string `[Char]` to numeric value so we can compute the resulst of each computation.

For this we use `read ... :: Double`.

So this works:

```haskell
ghci> calc "(4.5+5.6) * 3/2"
"15.149999999999999"
```

First we need one way to compute additions and substraction that are on the same prioritary level, done from left to right.

```haskell

subProtoCalc2 :: [Char] -> [Char] -> Int -> [Char]
subProtoCalc2 [] outxs _ = outxs
subProtoCalc2 (x:xs) outxs n
    | x == '+' =
            let val1raw = read . reverse $ takeBack2 (reverse outxs) 0 :: Double
                val2 = read $ takeBack2 xs 0 :: Double

                newoutxsRaw = reverse $ takeTailN2 (reverse outxs) 0

                (newoutxs, val1) =
                    if newoutxsRaw == "-"
                    then ("", -val1raw)
                    else (newoutxsRaw, val1raw)

                newxs = takeTailN2 xs 0

            in subProtoCalc2 newxs (newoutxs ++ show (val1 + val2)) (n + 1)

    | x == '-' && n /= 0 =
            let val1raw = read . reverse $ takeBack2 (reverse outxs) 0 :: Double
                val2 = read $ takeBack2 xs 0 :: Double

                newoutxsRaw = reverse $ takeTailN2 (reverse outxs) 0

                (newoutxs, val1) =
                    if newoutxsRaw == "-"
                    then ("", -val1raw)
                    else (newoutxsRaw, val1raw)

                newxs = takeTailN2 xs 0

            in subProtoCalc2 newxs (newoutxs ++ show (val1 - val2)) (n + 1)

    | otherwise =
            subProtoCalc2 xs (outxs ++ [x]) (n + 1)

```

`n` here is just the index that always increments to go to the next `Char`.

But it is not used for accessing char, for that we got data structure decomposition `(x:xs)`.

It just tells wether we should dtop the computation or not.

```haskell

| x == '-' && n /= 0 = 

```

Here, it just says that `-` is an operator ans not just describing the value.

This function handles this type of computation `"A OPERATOR B"`.

That's why we got:

```haskell

takeBack2 :: [Char] -> Int -> [Char]
takeBack2 [] _ = []
takeBack2 (x:xs) n 
    | not (x `elem` "+-*/") = (x:takeBack2 xs (n+1))
    | otherwise = if n == 0 then (x:takeBack2 xs (n+1)) else []

```

This just takes the first numeric value:

```haskell

ghci> takeBack2 "-4+6" 0
"-4"

```

And used in this context.

```haskell

let val1raw = read . reverse $ takeBack2 (reverse outxs) 0 :: Double
    val2 = read $ takeBack2 xs 0 :: Double

```

From 2 diferent sources.

Because remember when it does not match the operator `+` or `-`, it just constructs `outxs` with the `Char` it finds.

```haskell

| otherwise = subProtoCalc2 xs (outxs ++ [x])

```

But when it matches an operator, it just takes the first value, so the one already found in `outxs` and since it appended it, it must `reverse` it first and then input it in `takeBack2`.

Because it used `val1` for the computation, then this value must be removed from `outxs`.

```haskell

newoutxsRaw = reverse $ takeTailN2 (reverse outxs) 0

```

With:

```haskell

takeTailN2 :: [Char] -> Int -> [Char]
takeTailN2 [] _ = []
takeTailN2 (x:xs) n
    | not (x `elem` "+-*/") = takeTailN2 xs (n+1)
    | otherwise = if n == 0 then takeTailN2 xs (n+1) else  x:xs

```

Note, that here `takeTailN2` and `takeBack2` considers the sign of the value, that's important nd simplify A LOT of algorithmic work.

Same thing for `newxs`, because `val2` has been used.

```haskell

newxs = takeTailN2 xs 0

```

And we replace `val1` in `outxs` by the result for next recursive call.

```haskell

in subProtoCalc2 newxs (newoutxs ++ show (val1 - val2)) (n + 1)

```

Note that here it is not exactly `val1`, why ?

Because we need to check its sign, meaning if it comes with `"-"` attcahced as a sign and not an operator, meaning that `"-"` must be alone in `newoutxsRaw` (which is `newoutxs` after taking the last numeric value).

That's why we got:

```haskell

(newoutxs, val1) =
    if newoutxsRaw == "-"
    then ("", -val1raw)
    else (newoutxsRaw, val1raw)

```

### Execution model

Do you know where `subprotoCalc2` lives in the model ?

For now i can not tell you a clear view of the model but i want you to understand that is must executes just after `subProtocalc` which does the same thing than `subProtocalc2` but with `*` and `/`. 

That is totaly normal, because they are prioritary operators.

Here it is.

```haskell

subProtoCalc :: [Char] -> [Char] -> [Char]
subProtoCalc [] outxs = outxs
subProtoCalc (x:xs) outxs
    | x == '*' =
            let val1 = read . reverse $ takeBack2 (reverse outxs) 0 :: Double
                val2 = read $ takeBack2 xs 0 :: Double
                newoutxs = reverse $ takeTailN2 (reverse outxs) 0
                newxs = takeTailN2 xs 0
            in subProtoCalc newxs (newoutxs ++ show (val1 * val2))

    | x == '/' =
            let val1 = read . reverse $ takeBack2 (reverse outxs) 0 :: Double
                val2 = read $ takeBack2 xs 0 :: Double
                newoutxs = reverse $ takeTailN2 (reverse outxs) 0
                newxs = takeTailN2 xs 0
            in subProtoCalc newxs (newoutxs ++ show (val1 / val2))

    | otherwise =
            subProtoCalc xs (outxs ++ [x])

```

Note that it follows the same structure than `subProtoCalc2` btut does not need to check if `-` is an operator or just describing the value because it just cares about `*` and `/`.

Here is `protoCalc`, see the execution model respecting PEMDAS ?

```haskell

protoCalc :: [Char] -> [Char]
protoCalc xs =
    let step0 = clearOperator xs

        step1 = subProtoCalcIdentity step0 []
        step2 = clearOperator step1

        step3 = subProtoCalcExponent step2 []
        step4 = clearOperator step3

        step5 = subProtoCalc step4 [] -- we are here
        step6 = clearOperator step5

        step7 = subProtoCalc2 step6 [] 0
    in clearOperator step7

```

In fact you see that we are first computing result of multiplication and division operations.

#### Clearing Operators

Because each computation step can lead to a switch of sign for each valuee it has tom compute we need to normalize the string with `clearOperator`.

```haskell

clearOperator :: [Char] -> [Char]
clearOperator [] = []
clearOperator [x] = [x]
clearOperator (x1:x2:xs)
    | x1 == '+' && x2 == '-' = clearOperator ('-':xs)
    | x1 == '-' && x2 == '+' = clearOperator ('-':xs)
    | x1 == '+' && x2 == '+' = clearOperator ('+':xs)
    | x1 == '-' && x2 == '-' = clearOperator ('+':xs)
    | otherwise = x1 : clearOperator (x2:xs)

```

Explicit enough, if 2 consecutives `'-'` -> `'+'`.

If `'+'` then `'-'` or inversely -> `'-'`.

If not of the above -> `'+'`.

### Going back to the execution model

For example, look what it does:

```haskell

ghci> subProtoCalc "3+4*3-3/2" []
"3+12.0-1.5"

```
And after that we are just passing the result that now jst contains at most addition and / or substraction operators to `subProtocalc2`.

```haskell

ghci> subProtoCalc2 (subProtoCalc "3+4*3-3/2" []) [] 0
"13.5"

```

But, can we go further, because in PEMDAS, that's not explicitely said, but value identity is absolutely prioritary.

What i mean by that is that `EXP(X)`, `LOG(X)` or even Factorial `!`... must first be substituated by the value.

Because here that's not properly an operator but rather part of the value identity.

And between identity and multiplication and division,  we need to compute the exponentiation.

We do this with:

```haskell

subProtoCalcExponent :: [Char] -> [Char] -> [Char]
subProtoCalcExponent [] outxs = outxs
subProtoCalcExponent (x:xs) outxs
    | x == '^' = 
        let val1 = read . reverse $ takeBack2 (reverse outxs) 0 :: Double
            val2 = read $ takeBack2 xs 0 :: Double
            newoutxs = reverse $ takeTailN2 (reverse outxs) 0
            newxs = takeTailN2 xs 0 
        in subProtoCalcExponent newxs (newoutxs ++ (show (val1**(val2))))
    | otherwise = subProtoCalcExponent xs (outxs ++ [x])

```

Example.

```haskell

ghci> subProtoCalcExponent "1+3*4+4^2" []
"1+3*4+16.0"

```

Or:

```haskell

ghci> subProtoCalcExponent "1+3*4+4^-1.1" []
"1+3*4+0.217637640824031"

```

So, now identity !

```haskell

subProtoCalcIdentity :: [Char] -> [Char] -> [Char]
subProtoCalcIdentity [] outxs = outxs
subProtoCalcIdentity (x:xs) outxs
    | x == 'E' = 
        let val = read $ takeBack2 xs 0 :: Double
            newxs = takeTailN2 xs 0
        in subProtoCalcIdentity newxs (outxs ++ printf "%8f" ((exp(val)) :: Double) :: String)
    | x == 'L' = 
        let val = read $ takeBack2 xs 0 :: Double
            newxs = takeTailN2 xs 0
        in subProtoCalcIdentity newxs (outxs ++ printf "%8f" ((log(val)) :: Double) :: String)
    | x == '!' = 
        let val = read $ takeBack2 xs 0 :: Int
            newxs = takeTailN2 xs 0
        in subProtoCalcIdentity newxs (outxs ++ show (factorial val))
    | otherwise = subProtoCalcIdentity xs (outxs ++ [x])

```

Here, for convenience, the factorial expression is just `!X` and not `X!`.

Factoial function is just.

```haskell

factorial :: Int -> Int
factorial 1 = 1
factorial n = n * factorial (n - 1)

```

Example:

```haskell

ghci> subProtoCalcIdentity "1+3*4+4^-1.1+E4-!5" []
"1+3*4+4^-1.1+54.598150033144236-120"

```

### Final Pipeline

So, now we got the pipeline.

But the missing piece is the identification of prioritary computation inside parenthesis.

For that, we'll use the encoding that `parserPar` gave us.

```haskell

calc :: [Char] -> [Char]
calc xs = 
    let (ids, nums) = parserPar xs
        newxs = subCalc xs ids nums
    in protoCalc newxs

```

`calc` is the entry fucntion, the function that is exposed to the user.

But, here the important function is `subCalc`.

It takes the result of the toenization of parenthesis and the string to compute from.

```haskell

subCalc :: [Char] -> [Int] -> [Int] -> [Char]
subCalc xs [] [] = xs
subCalc xs ids nums =
    let curmax = myMax nums
        [id1, id2] = grepn2 curmax nums
        idstrt = ids !! id2
        idstop = ids !! id1

        xsstrt = if idstrt > 0
                 then getRangeList xs [0..(idstrt - 1)]
                 else []

        xsstop = if idstop + 1 < length xs
                 then getRangeList xs [(idstop + 1)..(length xs - 1)]
                 else []

        xsbetween = getRangeList xs [(idstrt + 1)..(idstop - 1)]
        rslt = protoCalc xsbetween

        newxs = xsstrt ++ rslt ++ xsstop

        (newids, newnums) = parserPar newxs
    in subCalc newxs newids newnums

```

So, what's nice about the encoding of parenthesis is `nums`, because it allows to identify most prioritary parenthesis, which are the most nested one, which are the one with the maximum value of pair.

So we just grep the index of the current maximum pair value inside `nums`.

Here.

```haskell

let curmax = myMax nums
    [id1, id2] = grepn2 curmax nums

```

Then we use those index to get the position of the parenthesis with `ids`, so we got the associated computation.

```haskell

idstrt = ids !! id2
idstop = ids !! id1

xsstrt = if idstrt > 0
         then getRangeList xs [0..(idstrt - 1)]
         else []

xsstop = if idstop + 1 < length xs
         then getRangeList xs [(idstop + 1)..(length xs - 1)]
         else []

xsbetween = getRangeList xs [(idstrt + 1)..(idstop - 1)]

```

And now we get its result.

```haskell

rslt = protoCalc xsbetween

```

And replace it in the new string to compute before reitering on it.

It means reparsing the parenthesis and repassing the string to the fucntion recursively.

```haskell

        newxs = xsstrt ++ rslt ++ xsstop

        (newids, newnums) = parserPar newxs
    in subCalc newxs newids newnums

```

That's all.

And a very naive approach.

### Benchmark & Results

Let's see how it preforms.

```haskell

ghci> calc "-6+-(-7+E-3/0.2)*4"
"21.00425863264272"

```

Compared to native:

```haskell

ghci> -6 + (-( -7 + exp (-3) / 0.2)) * 4
21.00425863264272

```

Great, now for bechmarks !

We'll compute 100K time this expression and see how fast it did it and how much it asked for allocation and how much the Haskell Garbage Collector was smart.

```haskell

benchCalc :: Int -> String -> String
benchCalc 1 expr = calc expr
benchCalc n expr =
    let r = calc expr
    in r `seq` benchCalc (n - 1) expr

main :: IO ()
main = do
    let expr = "-6+-(-7+E-3/0.2)*4"
    let result = benchCalc 100000 expr
    putStrLn result

```

### `seq`, the one that forces evaluation

Just a quick note about `seq` function.

In Haskell, `seq` is a special function used to force evaluation of something to weak head normal form.

Its type is:

```haskell

seq :: a -> b -> b

```

It looks weird, but the idea is:

```haskell

x `seq` y

```

means:

Evaluate `x` enough to know it is not bottom, then return `y`.

Simple example:

```haskell

main = print (1 `seq` 2)

```

Output:

```
2

```

Because `seq` evaluates `1`, then returns `2`.

More revealing:

```haskell

main = print (undefined `seq` 2)

```

This crashes:


```

*** Exception: Prelude.undefined

```

Because `seq` tries to evaluate the first argument before returning the second.

So `benchCalc` effectively creates a chain of function calls (`calc`) that must be evaluated.

But is that enough ?

### `deepseq` the honest `seq`

Because i also heard about:

```haskell

import Control.DeepSeq (deepseq)

```

What `deepseq` actualy does that `seq` does not ?

In Haskell, the difference is:

```haskell

seq     :: a -> b -> b
deepseq :: NFData a => a -> b -> b

```

`seq` forces only the outer constructor.

`deepseq` forces the value all the way down, recursively, as long as the type has an `NFData` instance.

`NFData` is a typeclass from Control.DeepSeq.

It means:

“Values of this type know how to be fully evaluated to normal form.”

The core method is:

```haskell

class NFData a where
    rnf :: a -> ()

```

`rnf` means reduce to normal form.

So when you write:

```haskell

x `deepseq` y

```

it is roughly:

```haskell

rnf x `seq` y

```

Meaning:

fully evaluate `x`, then return `y`

For simple types like Int, this is easy:

```haskell

rnf (42 :: Int) = ()

```

Because an Int is already a simple strict value once evaluated.

For a list:

```haskell

[1, 2, 3]

```

the `NFData` instance recursively forces:

the list spine
each element

So:

```haskell

[1, 2, 3] `deepseq` "done"

```

forces the whole list.

But:

```haskell

[1, undefined, 3] `deepseq` "done"

```

crashes, because the second element is forced.

`seq`: shallow evaluation

Example:

```haskell

xs = [1 + 2, 3 + 4, 5 + 6]

```

If you do:

```haskell

xs `seq` "done"

```

Haskell only checks that `xs` is not bottom and evaluates it enough to see the outer shape:

`(:)` thunk tail

So it knows:

`xs` is a non-empty list

But the elements are still not necessarily evaluated:

```haskell

1 + 2  still maybe not evaluated
3 + 4  still maybe not evaluated
5 + 6  still maybe not evaluated

```

So `seq` is shallow and `deepseq` is not.

But, do we need it here ?

Not really, because we do a lot of works that require the string to be constructed / evaluated inside the `calc` function, but that stills is a good practice in Haskell benchmark.

### Back to Benchmarks

Now we compile.

```bash

❯ ghc -O2 -rtsopts calculator.hs -o calculator
Loaded package environment from /home/juju/.ghc/x86_64-linux-9.4.7/environments/default
[1 of 2] Compiling Main             ( calculator.hs, calculator.o ) [Source file changed]
[2 of 2] Linking calculator [Objects changed]

```

`-rtsopts` flag is for teling that the binary will accept `RTS` options, `RTS` is the Haskell Runtime System that manages GC, heap, stack, lightweight threads, statistics, profiling hooks, etc.

So when we run with.

```bash
❯ ./calculator +RTS -s
```

means:

```
./calculator        run my program
+RTS               from here, arguments are for GHC's runtime system
-s                 print GC/runtime allocation statistics
```

Usually you can end with `-RTS`:

```bash
./calculator +RTS -s -RTS
```

For my case, since there are no program arguments after `-s`, leaving out `-RTS` is fine.

The important relation is:

```

compiled with -rtsopts  ->  executable accepts +RTS -s
compiled without it     ->  many RTS options are rejected

```

GHC’s docs say that `-rtsopts` with no argument is equivalent to `-rtsopts=all`, enabling all RTS option processing, while the default without it is only some, meaning basically safe/minimal options like `-?` and `--info`

And in ghc compiler, `-O2` is the maximum optimization flag.

So what are the results ?

```haskell

21.00425863264272
  19,924,132,880 bytes allocated in the heap
       4,784,504 bytes copied during GC
         108,264 bytes maximum residency (2 sample(s))
          29,400 bytes maximum slop
               6 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0      4778 colls,     0 par    0.019s   0.021s     0.0000s    0.0001s
  Gen  1         2 colls,     0 par    0.000s   0.000s     0.0002s    0.0003s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time    4.098s  (  4.096s elapsed)
  GC      time    0.019s  (  0.021s elapsed)
  EXIT    time    0.000s  (  0.002s elapsed)
  Total   time    4.118s  (  4.120s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    4,862,069,316 bytes per MUT second

  Productivity  99.5% of total user, 99.4% of total elapsed

```

Wow, 19 GB of allocations over the time of the programm running !!

```

  19,459,337,528 bytes allocated in the heap

```

But at peak moment, only `6MiB` was in used.

```

  6 MiB total memory in use (0 MB lost due to fragmentation)

```

A tons of very short live object were created.

The Garbage Collector do a very little of work.

Only about 4Mib of data was moved by the GC over the time.

So only about 4MiB of data lived long enough to be moved by the GC.

```

4,652,384 bytes copied during GC

```

and its peak is arround.

```
         
107,416 bytes maximum residency (2 sample(s))

```

We also got:

```

29,400 bytes maximum slop

```

Which is maximum wasted heap space due to imperfect packing/alignment/block granularity. 

Now, how to explaine the big difference betwen these two?

```

  19,459,337,528 bytes allocated in the heap

```

AND

```

  4,652,384 bytes copied during GC

```

Which is wasted/unused heap space inside allocated blocks, caused by the runtime’s block allocation granularity.

It is mostly GHC’s runtime system / generational GC discovering that at runtime.

For temporary `reverse`, `takeBack2`, `++`, `show`, etc., the flow is more like:


1. Program allocates many temporary lists/strings.
2. They are used for a very short time.
3. After that, nothing points to them anymore.
4. Minor GC runs.
5. GC follows the live pointers from roots: stack, registers, globals, etc.
6. It copies only objects still reachable.
7. Everything not reachable is garbage.
8. The whole old nursery region can be reused.

So the GC does not say:

this reverse object is short-lived, free exactly this object

It says more like:

I found the few objects that are still alive.

Everything else in this nursery is dead.

Reset/reuse the nursery.

That’s why it’s so fast.

GHC assumes most new objects die young. This is usually true in functional programs because you create lots of temporary values during expression evaluation.

So in this case:

```haskell
reverse outxs
takeBack2 xs 0
newoutxs ++ show value
```

probably creates tons of short-lived list cells and strings. But by the time GC checks, most of them are unreachable. Therefore:

- allocated: huge
- copied by GC: tiny

So the clean mental model is:

```

GHC compiler:
  tries to optimize away some allocations if possible

GHC runtime / GC:
  manages allocated heap objects
  keeps reachable objects
  discards unreachable nursery memory cheaply

```

## Naive version, but better representation

### Changing representation of List `[Char]`

A list in Haskell is basically:

```haskell

data List a
    = Empty
    | Cons a (List a)

```

That we construct like that:

```haskell

ghci> 1 : 2: 3 : []
[1,2,3]

```

That is in fact a linked list, not ideal for data compactnes and acessing speed.

So we can change the representation from standard list `ByteString`, which is an array of data.

Coming from:

```haskell

import qualified Data.ByteString.Char8 as B
import Data.ByteString.Char8 (ByteString)

```

Note, here we are importing the `Data.ByteString.Char8` "class" that provides usefull functio to work with `ASCII` characters that works well with `ByteString`, for convertions between `[Char]` etcetera.

All is scoped around `B` apart from the type itself it depends on with:

```haskell

import Data.ByteString.Char8 (ByteString)

```

#### What's new ?

So for function signature, no need to do `B.ByteString`.

We keep the exact same architecture, just tweak the signature and the methods, for example from `reverse` to `B.reverse` etcetera.

Also, no need for custom `getRangeList` which is inneficient because need workng on linked list (overhead for acessing).

Here, we can directly do:

```haskell

xsstrt = B.take idstrt xs
xsstop = B.drop (idstop + 1) xs

```

Example for `drop` method.

```haskell

ghci> B.drop 3 $ B.pack "abcdefghikklmnopqrst"
"defghikklmnopqrst"

```

Example for `take` method.

```haskell

ghci> B.take 3 $ B.pack "abcdefghikklmnopqrst"
"abc"

```

Also the construction of `ByteString` is different.

For example for appending a `Char` (with `Char8` `snoc` method).

```haskell

ghci> B.snoc (B.pack "abcde") 'f'
"abcdef"

```

And the constructor is `cons`:

```haskell

ghci> B.cons 'a' $ B.pack "bcdef"
"abcdef"

```

And surely for pattenr matching which we do with `(x:xs)` -> head + tail is different here.

We still have the concept of head and tailbut that is done like:

```haskell

takeTailN2 :: ByteString -> Int -> ByteString
takeTailN2 bs n = 
    case B.uncons bs of
        
        Nothing -> B.empty

        Just (x, xs)
            | not (x `elem` "+-*/^") -> takeTailN2 xs (n+1)
            | otherwise -> if n == 0 then takeTailN2 xs (n+1) else B.cons x xs

```

So here the `case ... of` replace the role of basic pattern matching.

And the associated logic after pattern matching inside `case ... of` is done with `->`.

Because remember the old `TailN2` was:

```haskell

takeTailN2 :: [Char] -> Int -> [Char]
takeTailN2 [] _ = []
takeTailN2 (x:xs) n
    | not (x `elem` "+-*/") = takeTailN2 xs (n+1)
    | otherwise = if n == 0 then takeTailN2 xs (n+1) else  x:xs


```

Completely different synthax for pattern matching but same logic.

#### Actual Code

Here it is.

```haskell

import Text.Printf

import qualified Data.ByteString.Char8 as B
import Data.ByteString.Char8 (ByteString)

factorial :: Int -> Int
factorial 1 = 1
factorial n = n * factorial (n - 1)

grepn2 :: (Eq a) => a -> [a] -> [Int]
grepn2 cmp xs = subGrepn2 xs cmp 0 []

subGrepn2 :: (Eq a) => [a] -> a -> Int -> [Int] -> [Int]
subGrepn2 [] _ _ nxs = nxs
subGrepn2 (x:xs) cmp n nxs
    | cmp == x  = subGrepn2 xs cmp (n + 1) (n:nxs)
    | otherwise = subGrepn2 xs cmp (n + 1) nxs

myMax :: (Ord a) => [a] -> a
myMax xs = subMyMax xs (head xs)

subMyMax :: (Ord a) => [a] -> a -> a
subMyMax [] cmp = cmp
subMyMax (x:xs) cmp = 
    let cmp2 = if cmp >= x
              then cmp
              else x
    in subMyMax xs cmp2

parserPar :: ByteString -> ([Int], [Int])
parserPar xs = subParserPar xs [] [] [] 0 0

subParserPar :: ByteString -> [Int] -> [Int] -> [Int] -> Int -> Int
             -> ([Int], [Int])
subParserPar bs ids nums valxs n n2 =
    case B.uncons bs of
        Nothing ->
            (ids, nums)

        Just (x, xs)
            | x == '(' ->
                let newids = ids ++ [n]
                    newnums = nums ++ [n2]
                    newvalxs = map (\v -> v + 1) valxs
                    newvalxs2 = newvalxs ++ [1]
                in subParserPar xs newids newnums newvalxs2 (n + 1) (n2 + 1)

            | x == ')' ->
                let newvalxs = map (\v -> v - 1) valxs
                    idx = findFirstZero (reverse newvalxs) 0
                    idx2 = length valxs - idx - 1
                    newids = ids ++ [n]
                    newnums = nums ++ [nums !! idx2]
                in subParserPar xs newids newnums (newvalxs ++ [0]) (n + 1) n2

            | otherwise ->
                subParserPar xs ids nums valxs (n + 1) n2

findFirstZero :: [Int] -> Int -> Int
findFirstZero (xi:xsi) n
              | xi == 0 = n
              | otherwise = findFirstZero xsi (n + 1)

calc :: ByteString -> ByteString
calc xs = 
    let (ids, nums) = parserPar xs
        newxs = subCalc xs ids nums
    in protoCalc newxs
    
subCalc :: ByteString -> [Int] -> [Int] -> ByteString
subCalc xs [] [] = xs
subCalc xs ids nums =
    let curmax = myMax nums
        [id1, id2] = grepn2 curmax nums

        idstrt = ids !! id2
        idstop = ids !! id1

        xsstrt = B.take idstrt xs
        xsstop = B.drop (idstop + 1) xs
        xsbetween = B.take (idstop - idstrt - 1) (B.drop (idstrt + 1) xs)

        rslt = protoCalc xsbetween

        newxs = xsstrt <> rslt <> xsstop

        (newids, newnums) = parserPar newxs
    in subCalc newxs newids newnums

protoCalc :: ByteString -> ByteString
protoCalc xs =
    let step0 = clearOperator xs

        step1 = subProtoCalcIdentity step0 B.empty
        step2 = clearOperator step1

        step3 = subProtoCalcExponent step2 B.empty
        step4 = clearOperator step3

        step5 = subProtoCalc step4 B.empty
        step6 = clearOperator step5

        step7 = subProtoCalc2 step6 B.empty 0
    in clearOperator step7

takeBack2 :: ByteString -> Int -> ByteString
takeBack2 bs n = 
    case B.uncons bs of
        
        Nothing -> B.empty

        Just (x, xs) 
            | not (x `elem` "+-*/^") -> B.cons x (takeBack2 xs (n+1))
            | otherwise -> if n == 0 then B.cons x (takeBack2 xs (n+1)) else B.empty

takeTailN2 :: ByteString -> Int -> ByteString
takeTailN2 bs n = 
    case B.uncons bs of
        
        Nothing -> B.empty

        Just (x, xs)
            | not (x `elem` "+-*/^") -> takeTailN2 xs (n+1)
            | otherwise -> if n == 0 then takeTailN2 xs (n+1) else B.cons x xs

subProtoCalc :: B.ByteString -> B.ByteString -> B.ByteString
subProtoCalc bs outxs =
    case B.uncons bs of

        Nothing ->
            outxs

        Just (x, xs)
            | x == '*' ->
                let val1 =
                        read . B.unpack . B.reverse $
                            takeBack2 (B.reverse outxs) 0 :: Double

                    val2 =
                        read . B.unpack $
                            takeBack2 xs 0 :: Double

                    newoutxs =
                        B.reverse $ takeTailN2 (B.reverse outxs) 0

                    newxs =
                        takeTailN2 xs 0

                    result =
                        B.pack (show (val1 * val2))

                in subProtoCalc newxs (newoutxs <> result)

            | x == '/' ->
                let val1 =
                        read . B.unpack . B.reverse $
                            takeBack2 (B.reverse outxs) 0 :: Double

                    val2 =
                        read . B.unpack $
                            takeBack2 xs 0 :: Double

                    newoutxs =
                        B.reverse $ takeTailN2 (B.reverse outxs) 0

                    newxs =
                        takeTailN2 xs 0

                    result =
                        B.pack (show (val1 / val2))

                in subProtoCalc newxs (newoutxs <> result)

            | otherwise ->
                subProtoCalc xs (B.snoc outxs x)

clearOperator :: B.ByteString -> B.ByteString
clearOperator bs =
    case B.uncons bs of
        Nothing ->
            B.empty

        Just (x1, rest) ->
            case B.uncons rest of
                Nothing ->
                    B.singleton x1

                Just (x2, xs)
                    | x1 == '+' && x2 == '-' ->
                        clearOperator (B.cons '-' xs)

                    | x1 == '-' && x2 == '+' ->
                        clearOperator (B.cons '-' xs)

                    | x1 == '+' && x2 == '+' ->
                        clearOperator (B.cons '+' xs)

                    | x1 == '-' && x2 == '-' ->
                        clearOperator (B.cons '+' xs)

                    | otherwise ->
                        B.cons x1 (clearOperator (B.cons x2 xs))

subProtoCalc2 :: ByteString -> ByteString -> Int -> ByteString
subProtoCalc2 bs outxs n =
    case B.uncons bs of
        Nothing ->
            outxs

        Just (x, xs)
            | x == '+' ->
                let val1raw =
                        read . B.unpack . B.reverse $
                            takeBack2 (B.reverse outxs) 0 :: Double

                    val2 =
                        read . B.unpack $
                            takeBack2 xs 0 :: Double

                    newoutxsRaw =
                        B.reverse $ takeTailN2 (B.reverse outxs) 0

                    (newoutxs, val1) =
                        if newoutxsRaw == B.singleton '-'
                        then (B.empty, -val1raw)
                        else (newoutxsRaw, val1raw)

                    newxs =
                        takeTailN2 xs 0

                    result =
                        B.pack (show (val1 + val2))

                in subProtoCalc2 newxs (newoutxs <> result) (n + 1)

            | x == '-' && n /= 0 ->
                let val1raw =
                        read . B.unpack . B.reverse $
                            takeBack2 (B.reverse outxs) 0 :: Double

                    val2 =
                        read . B.unpack $
                            takeBack2 xs 0 :: Double

                    newoutxsRaw =
                        B.reverse $ takeTailN2 (B.reverse outxs) 0

                    (newoutxs, val1) =
                        if newoutxsRaw == B.singleton '-'
                        then (B.empty, -val1raw)
                        else (newoutxsRaw, val1raw)

                    newxs =
                        takeTailN2 xs 0

                    result =
                        B.pack (show (val1 - val2))

                in subProtoCalc2 newxs (newoutxs <> result) (n + 1)

            | otherwise ->
                subProtoCalc2 xs (B.snoc outxs x) (n + 1)

subProtoCalcIdentity :: ByteString -> ByteString -> ByteString
subProtoCalcIdentity bs outxs = 
    case B.uncons bs of

        Nothing -> outxs

        Just(x, xs)
            | x == 'E' -> 
                let val = read . B.unpack $ takeBack2 xs 0 :: Double
                    newxs = takeTailN2 xs 0
                    result = B.pack (printf "%8f" (exp val) :: String)
                in subProtoCalcIdentity newxs (outxs <> result)
            | x == 'L' -> 
                let val = read . B.unpack $ takeBack2 xs 0 :: Double
                    newxs = takeTailN2 xs 0
                    result = B.pack (printf "%8f" (log val) :: String)
                in subProtoCalcIdentity newxs (outxs <> result)
            | x == '!' ->
                let val = read . B.unpack $ takeBack2 xs 0 :: Int
                    newxs = takeTailN2 xs 0
                    result = B.pack $ show (factorial val)
                in subProtoCalcIdentity newxs (outxs <> result)
            | otherwise -> subProtoCalcIdentity xs (B.snoc outxs x)


subProtoCalcExponent :: ByteString -> ByteString -> ByteString
subProtoCalcExponent bs outxs = 
    case B.uncons bs of

        Nothing -> outxs

        Just(x, xs)
            | x == '^' ->
                let val1 = read . B.unpack . B.reverse $ takeBack2 (B.reverse outxs) 0 :: Double
                    val2 = read . B.unpack $ takeBack2 xs 0 :: Double
                    newoutxs = B.reverse $ takeTailN2 (B.reverse outxs) 0
                    newxs = takeTailN2 xs 0 
                    result = B.pack (show (val1**(val2)))
                in subProtoCalcExponent newxs (newoutxs <> result)
            | otherwise -> subProtoCalcExponent xs (B.snoc outxs x)

```

Note i could have done above:

When you want to debug with "printing", do it with traces, for example add the import.

```haskell

import Debug.Trace

```

And here is the fucntion where it is good to print intermediate results.


```haskell

protoCalc :: [Char] -> [Char]
protoCalc xs =
    let step0 = clearOperator xs

        step1 = subProtoCalcIdentity step0 []
        step2 = clearOperator step1

        step3 = subProtoCalcExponent step2 []
        step4 = clearOperator step3

        step5 = subProtoCalc step4 []
        step6 = clearOperator step5

        step7 = subProtoCalc2 step6 [] 0
    in trace ("step0 input:    " ++ step0) $
       trace ("step1 identity: " ++ step1) $
       trace ("step2 clear:    " ++ step2) $
       trace ("step3 exponent: " ++ step3) $
       trace ("step4 clear:    " ++ step4) $
       trace ("step5 */:       " ++ step5) $
       trace ("step6 clear:    " ++ step6) $
       trace ("step7 +-:       " ++ step7) $
       clearOperator step7

```

And we still in pure stateless state lol, -> just intermediate `trace` functions.

### Benchmarks & Results - Architecture 1 - Representation 2

Same compiling and execution than for the first one.

```haskell

21.00425863264272
  14,051,918,568 bytes allocated in the heap
       2,341,552 bytes copied during GC
          80,368 bytes maximum residency (2 sample(s))
          29,512 bytes maximum slop
               6 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0      3359 colls,     0 par    0.018s   0.019s     0.0000s    0.0001s
  Gen  1         2 colls,     0 par    0.000s   0.000s     0.0002s    0.0003s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time    3.357s  (  3.355s elapsed)
  GC      time    0.018s  (  0.019s elapsed)
  EXIT    time    0.000s  (  0.006s elapsed)
  Total   time    3.376s  (  3.380s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    4,185,492,983 bytes per MUT second

  Productivity  99.5% of total user, 99.3% of total elapsed

```

That's already better.

- total of heap allocation over time = `19GB` -> `14GB`

- GC's bytes copied = -> `4.7MiB` -> `2.3MiB`

- max bytes copied at a moment = `107.4KiB` -> `80.37Kib`

- and the wasted memory = `29.4KiB` -> `29.5KiB`

So significantively better performance, but still slow.

## Tokenizer and Direct WaterFall Evaluation

Instead of applying logic to strings on the fly, we just pay a small cost of tokenizing the string into `Tokens` and then we apply logic at an extremely lower cost that will avoid creating temprorary object for nothing.

We will just evaluate the Tokens ONCE !

And not replacing parenthesis computations with its result and then re-evaluating this one (parenthesis tokenization + parsing of values).

We still work with `ByteString` since it gave use clear advantages for data representation.

### The Tokenizer

First, we just pay a small cost of tokenizing, but not only parenthesis, ALL.

ALL is of course parenthesis, but also values and operators.

There won't be a weird representation of parnthesis like the previous `parserPar` had.

No just raw tokens in a List.

#### Imports 

First the infamous import for `ByteString`.

```haskell

import qualified Data.ByteString.Char8 as B
import Data.ByteString.Char8 (ByteString)

```

Then, an import for functions that will use, `isDigit` tells us if the current `Char` is a digit or not:


```haskell

import Data.Char (isDigit, isSpace)

```

For example:

```haskell

ghci> import Data.Char (isDigit)
ghci> isDigit '.'
False
ghci> isDigit '1'
True

```

And `isSpace`:

```haskell

ghci> isSpace ' '
True

```

#### Structure for a Token

We then define our own **type** that can take several values, operators, Value, Identity (Exp, Log...), Parenthesis...

```haskell

data Token
    = TNum Double
    | TPlus
    | TMinus
    | TMul
    | TDiv
    | TPow
    | TExp
    | TLog
    | TLParen
    | TRParen
    deriving (Show, Eq)

```

Of course each value it takes must be showable `Show` and must be comparable `Eq`.

#### Logic

Here is the code.

```haskell
tokenize :: ByteString -> Either String [Token]
tokenize bs0 =
    let bs = B.dropWhile isSpace bs0
    in if B.null bs
       then Right []
       else if B.isPrefixOf (B.pack "exp") bs
            then (TExp :) <$> tokenize (B.drop 3 bs)
       else if B.isPrefixOf (B.pack "log") bs
            then (TLog :) <$> tokenize (B.drop 3 bs)
       else
            case B.uncons bs of
                Nothing ->
                    Right []

                Just (x, xs)
                    | isDigit x || x == '.' ->
                        let (numTxt, rest) =
                                B.span (\c -> isDigit c || c == '.') bs
                        in case reads (B.unpack numTxt) :: [(Double, String)] of
                            [(n, "")] -> --parser succeeds
                                (TNum n :) <$> tokenize rest

                            _ ->
                                Left ("Invalid number: " ++ B.unpack numTxt)

                    | x == '+' ->
                        (TPlus :) <$> tokenize xs

                    | x == '-' ->
                        (TMinus :) <$> tokenize xs

                    | x == '*' ->
                        (TMul :) <$> tokenize xs

                    | x == '/' ->
                        (TDiv :) <$> tokenize xs

                    | x == '^' ->
                        (TPow :) <$> tokenize xs

                    | x == 'E' ->
                        (TExp :) <$> tokenize xs

                    | x == 'L' ->
                        (TLog :) <$> tokenize xs

                    | x == '(' ->
                        (TLParen :) <$> tokenize xs

                    | x == ')' ->
                        (TRParen :) <$> tokenize xs

                    | otherwise ->
                        Left ("Unknown character: " ++ [x])


```

We just consumes tokens that do not interest us (which is space) with:

```haskell

    let bs = B.dropWhile isSpace bs0

```

Before ingesting tokens.

So about the identity of the value, we'll use

```haskell

      else if B.isPrefixOf (B.pack "exp") bs
            then (TExp :) <$> tokenize (B.drop 3 bs)
       else if B.isPrefixOf (B.pack "log") bs
            then (TLog :) <$> tokenize (B.drop 3 bs)

```

So just checking if the current start of the ByteString matches "exp" or "log", if yes just appending a Token `TExp` or `TLog` to the Tokens List and dropping the 3 characters that compose these tokens, with a recursive call.

Example of Exonential.

```haskell
            
    then (TExp :) <$> tokenize (B.drop 3 bs)

```

If tthat does not match, then we just unconstruct the token and pattern match on it.


```haskell

    case B.uncons bs of

```

If this outputs nothing, then we know that we consume all the characters, hence this is the end of the recursive calls.

```haskell

Nothing ->
    Right []

```

Of course we just check the head for a known simple char token:

```haskell

| x == '+' ->
    (TPlus :) <$> tokenize xs

| x == '-' ->
    (TMinus :) <$> tokenize xs

| x == '*' ->
    (TMul :) <$> tokenize xs

| x == '/' ->
    (TDiv :) <$> tokenize xs

| x == '^' ->
    (TPow :) <$> tokenize xs

| x == 'E' ->
    (TExp :) <$> tokenize xs

| x == 'L' ->
    (TLog :) <$> tokenize xs

| x == '(' ->
    (TLParen :) <$> tokenize xs

| x == ')' ->
    (TRParen :) <$> tokenize xs


```

But for more complex token that may describe a numeric value, here is the code:

```haskell

| isDigit x || x == '.' ->
    let (numTxt, rest) =
            B.span (\c -> isDigit c || c == '.') bs
    in case reads (B.unpack numTxt) :: [(Double, String)] of
        [(n, "")] -> --parser succeeds
            (TNum n :) <$> tokenize rest

        _ ->
            Left ("Invalid number: " ++ B.unpack numTxt)

```

With that:

```haskell

| isDigit x || x == '.' ->

```

We consider for example `0.23` or `.023` being a numeric value.

But to be sure of it we go further with `B.span` method.

```haskell

    let (numTxt, rest) =
            B.span (\c -> isDigit c || c == '.') bs

```

It just creates a String from a another String from left to right while the condition is True.

And it also outputs the rest.

Think of it like a `B.take idx` and a `B.drop idx` where `idx` is computed beeing incremented while the condition is True from the first `Char` on the input `ByteString` `bs`. 

And yess, `c` is a valid `Char` extracted from `bs` which is a `ByteString`.

Example:

```haskell

ghci> B.span (\x -> x `elem` "PA") (B.pack "PARIS")
("PA","RIS")

```

##### The infamous `reads` function

This one s tricky.

Remember when we convert from String to Numeric value, like Double with:

```haskell

ghci> read "1.3" :: Double
1.3

```

The `reads` function will do approxiately the same but Char by Char until it does not succed anymore to convert to the given type.

In the parser, on the String `B.unpack numTxt` and try to convert it to the type `Double` (for each Char).

But why is:

```haskell

reads (B.unpack numTxt) :: [(Double, String)]

```

then ?

That's because `reads` will output a list of pairs.

The pairs are:

```haskell
(TypeYouWantToConvertTo, RemaindingString)
```

And now i hear you saying:

"Okok, but why a List of pairs, i mean here we jst want to convert to a Type, it's explicit enough!"

Right, in this case it will indeed output a singleton with only one pair.

This is also why we check like that to see if our numeric value parsing succeded:

```haskell

[(n, "")] -> --parser succeeds -- singleton here
    (TNum n :) <$> tokenize rest

_ ->
    Left ("Invalid number: " ++ B.unpack numTxt)

```

But `reads` is more general, and in some custom type a user can define the logic of `read InputString` to a custom type can succedd but givng 2 or more values for its custom type.

Imagine this custom type:

```haskell

data Weird = A | B
    deriving Show

```

Now we'll define their behaviour when a `read InputString :: Weird` is applied. 

In order to do that, we just import.

```haskell

import Text.ParserCombinators.ReadP

```

That gives us the opportunity to do so by defining a special instance for type `Weird`.

```haskell

instance Read Weird where
    readsPrec _ input =
        readP_to_S parser input
      where
        parser =
            (string "France" >> return A)
            +++
            (string "France" >> return B)

```

Because `read` will use `readsPrec` so we just define the function when it tries to convert to type `Weird`.

We see here that it must call `readP_to_S parser` on `input`.

Where `parser` is THE custom parser logic we implement to tell which values of the type `Weird` a `read` on a String should return depending on the value of `String`.

Here, we just say that it should at the mean time return `A` and `B` when the string starts with "France".

Then when we apply `reads` with this casting `[(Weird, String)]`.

```haskell

ghci> reads "France is where i live" :: [(Weird, String)]
[(A," is where i live"),(B," is where i live")]

```

You see that it returned one pair per type found. 

### The Parser (With direct evaluator)

So, we just have tokenized our string, great !

But now we have to evaluate it !

How to do it then ?

I mean we still have to preserver the PEMDAS.

And also we DO NOT WANT to evaluate the input more than one time.

So a big shift in the mental odel is necessary.

We will do a weterfall evaluation.

What i mean by that is starting from the least prioritary to the most prioritary operations.

Evaluating like that allow us to evaluate the input once, because note what happens when we do that conceptually.

1. Evaluation of `+` and `-` (left to right)

And there maybe i come accross a token that belongs to another prioritary level, a token that for this level i do not know so i'll ask the next level to evaluate it.

I do this every time in fact even at the very beginning with `parseExpr`.

With this concept, `B.pack "3^2+3*2+(5-6)"` can be properly evaluated.

That's what i call a **waterfall evaluation**.

```haskell

parseExpr :: [Token] -> Either String (Double, [Token])
parseExpr tokens = do
    (lhs, rest) <- parseTerm tokens
    parseExprRest lhs rest

parseExprRest :: Double -> [Token] -> Either String (Double, [Token])
parseExprRest acc tokens =
    case tokens of
        TPlus : rest -> do
            (rhs, rest') <- parseTerm rest
            parseExprRest (acc + rhs) rest'

        TMinus : rest -> do
            (rhs, rest') <- parseTerm rest
            parseExprRest (acc - rhs) rest'

        _ ->
            Right (acc, tokens)

```

2. Evaluating `*` and `/` (left to right)

```haskell

parseTerm :: [Token] -> Either String (Double, [Token])
parseTerm tokens = do
    (lhs, rest) <- parsePower tokens
    parseTermRest lhs rest

parseTermRest :: Double -> [Token] -> Either String (Double, [Token])
parseTermRest acc tokens =
    case tokens of
        TMul : rest -> do
            (rhs, rest') <- parsePower rest
            parseTermRest (acc * rhs) rest'

        TDiv : rest -> do
            (rhs, rest') <- parsePower rest
            parseTermRest (acc / rhs) rest'

        _ ->
            Right (acc, tokens)

```

Same thing, the only architectural difference here is that i explicitely disociated the function that will parse `*` and `/` from the call to the next prioritary level, because i must do it anyway, so i do once when `parseTerm` is called.

3. Evaluating exponentialtion (power)

Here i'm at the most prioritary level operator wise, so just before computing i will evaluate the identity.

```haskell

parsePower :: [Token] -> Either String (Double, [Token])
parsePower tokens = do
    (base, rest) <- parseUnary tokens
    case rest of
        TPow : rest' -> do
            (exponent, rest'') <- parsePower rest'
            Right (base ** exponent, rest'')

        _ ->
            Right (base, rest)

```

4. Evaluating `exp`, `log`, but also normalizin operators.

```haskell

parseUnary :: [Token] -> Either String (Double, [Token])
parseUnary tokens =
    case tokens of
        TPlus : rest ->
            parseUnary rest

        TMinus : rest -> do -- impressive, very nice
            (v, rest') <- parseUnary rest
            Right (-v, rest')

        TExp : rest -> do
            (v, rest') <- parseUnary rest
            Right (exp v, rest')

        TLog : rest -> do
            (v, rest') <- parseUnary rest
            Right (log v, rest')

        _ ->
            parsePrimary tokens

```

And after that if i again find a token i do not know for this level, i call `parsePrimary`.

```haskell

_ ->
    parsePrimary tokens

```

5. Here this is the absolute prioritary level !

```haskell

parsePrimary :: [Token] -> Either String (Double, [Token])
parsePrimary tokens =
    case tokens of
        TNum n : rest ->
            Right (n, rest)

        TLParen : rest -> do
            (v, rest') <- parseExpr rest
            case rest' of
                TRParen : rest'' ->
                    Right (v, rest'')

                _ ->
                    Left "Expected closing parenthesis"

        [] ->
            Left "Unexpected end of expression"

        tok : _ ->
            Left ("Unexpected token: " ++ show tok)

```

In one case, it can just return a `TNum`, when for example caled from `parsePower` -> `parseUnary` -> `ParsePrimary`.

```haskell

TNum n : rest ->
    Right (n, rest)

```

But, in another case it can encounter an opening parenthesis, then it must call te first priritary level for the computation inside the parenthesis:

```haskell

TLParen : rest -> do
    (v, rest') <- parseExpr rest
    case rest' of
        TRParen : rest'' ->
            Right (v, rest'')

        _ ->
            Left "Expected closing parenthesis"

```

And, that's also here that i can be sure to return error from unknown tokens for example or ending abruptly.

```haskell

[] ->
    Left "Unexpected end of expression"

tok : _ ->
    Left ("Unexpected token: " ++ show tok)

```

6. The entry point.

It's is just.

```haskell

calc :: ByteString -> Either String Double
calc input = do
    tokens <- tokenize input
    parseCalc tokens

```

With `parseCalc` doing the last error handling (when tokens can still be there).

```haskel

parseCalc :: [Token] -> Either String Double
parseCalc tokens =
    case parseExpr tokens of
        Left err ->
            Left err

        Right (result, rest) ->
            case rest of
                [] ->
                    Right result

                _ ->
                    Left ("Unexpected tokens at end: " ++ show rest)

```

### Benchmark & Results

First, we just test it.

```haskell

ghci> calc $ B.pack "-6+-(-7+exp-3/0.2)*4"
Right 21.00425863264272

```
Or with default `exp` synthax.

```haskell

ghci> calc $ B.pack "-6+-(-7+exp-3/0.2)*4"
Right 21.00425863264272

```

Good, now the benchmarks !


```bash

❯ ghc -O2 -rtsopts calculator4.hs -o calculator4
Loaded package environment from /home/juju/.ghc/x86_64-linux-9.4.7/environments/default
[1 of 2] Compiling Main             ( calculator4.hs, calculator4.o ) [Source file changed]
[2 of 2] Linking calculator4 [Objects changed]

```

```bash

21.00425863264272
   2,026,537,624 bytes allocated in the heap
         139,536 bytes copied during GC
          44,328 bytes maximum residency (2 sample(s))
          33,496 bytes maximum slop
               6 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0       489 colls,     0 par    0.001s   0.001s     0.0000s    0.0000s
  Gen  1         2 colls,     0 par    0.000s   0.000s     0.0002s    0.0003s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time    0.352s  (  0.352s elapsed)
  GC      time    0.002s  (  0.002s elapsed)
  EXIT    time    0.000s  (  0.006s elapsed)
  Total   time    0.354s  (  0.360s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    5,757,237,520 bytes per MUT second

  Productivity  99.4% of total user, 97.7% of total elapsed

```

Damn it.

Massive improovements.

## Conclusion

`Tokenizer + Parser + WaterFall Evaluator` allocates ~10.3× less heap than `calculator`.

`Tokenizer + Parser + WaterFall Evaluator` runs ~13.2× faster than `calculator`.

The speedup mostly comes from doing much less temporary string/list allocation work, not from reducing GC overhead, because GC time was already tiny in all three versions.

That's why Parsers were invented.



