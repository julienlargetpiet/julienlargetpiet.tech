## Context

In this project, we build a **complete calculator** in Haskell that can evaluate normal
arithmetic expressions written in _parenthesis notation_ (e.g. `(3+5)*(2-(4/2))`) as string of course.
This goes far beyond Reverse Polish Notation: we now need to handle nested parentheses, operator precedence,
and negative values, all from scratch.

This is a programm i like to do when discovering a language because algorithmically speaking it ia not really eleguant, so here we test the elegantness of a language measured on how much we can condense code.

## Fundamental functions

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

## Parenthesis tokenization

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


## Proto computation

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
        let val1 = read . reverse . takeBack . reverse $ outxs :: Double
            val2 = read . takeBack $ xs :: Double
            newoutxs = reverse . takeTailN . reverse $ outxs
            newxs = takeTailN xs
        in if null newoutxs 
           then subProtoCalc2 newxs (newoutxs ++ (show (val1 + val2))) (n + 1)
           else if last newoutxs /= '-'
           then subProtoCalc2 newxs (newoutxs ++ (show (val1 + val2))) (n + 1)
           else if val1 > val2
                then subProtoCalc2 newxs (newoutxs ++ (show (val1 - val2))) (n + 1)
                else subProtoCalc2 newxs (init newoutxs ++ (show (val2 - val1))) (n + 1)
    | x == '-' && n /= 0 = 
        let val1 = read . reverse . takeBack . reverse $ outxs :: Double
            val2 = read . takeBack $ xs :: Double
            newoutxs = reverse . takeTailN . reverse $ outxs
            newxs = takeTailN xs
        in if null newoutxs 
           then subProtoCalc2 newxs (newoutxs ++ (show (val1 - val2))) (n + 1)
           else if last newoutxs /= '-'
           then subProtoCalc2 newxs (newoutxs ++ (show (val1 - val2))) (n + 1)
           else subProtoCalc2 newxs (newoutxs ++ (show (val1 + val2))) (n + 1)
    | otherwise = subProtoCalc2 xs (outxs ++ [x]) (n + 1)

```

`n` here is just the index that always increments to go to the next `Char`.

But it is not used for accessingchar, for that we got data structure decomposition `(x:xs)`.

It just tells wether we should dtop the computation or not.

```haskell

| x == '-' && n /= 0 = 

```

Here, it just says that `-` is an operator ans not just describing the value.

```haskell

then subProtoCalc2 newxs (newoutxs ++ (show (val1 + val2))) (n + 1)
else if last newoutxs /= '-'
then subProtoCalc2 newxs (newoutxs ++ (show (val1 + val2))) (n + 1)
else if val1 > val2
     then subProtoCalc2 newxs (newoutxs ++ (show (val1 - val2))) (n + 1)
     else subProtoCalc2 newxs (init newoutxs ++ (show (val2 - val1))) (n + 1)


then subProtoCalc2 newxs (newoutxs ++ (show (val1 - val2))) (n + 1)
else if last newoutxs /= '-'
then subProtoCalc2 newxs (newoutxs ++ (show (val1 - val2))) (n + 1)
else subProtoCalc2 newxs (newoutxs ++ (show (val1 + val2))) (n + 1)

otherwise = subProtoCalc2 xs (outxs ++ [x]) (n + 1)

```

This functions handle this type of computation `"A OPERATOR B"`.

That's why we got:

```haskell

takeBack (x:xs) 
    | not (x `elem` "+-*/") = (x:takeBack xs)
    | otherwise = []

```

This just takes the first numeric value:

```haskell
ghci> takeBack "1.3+5-3"
"1.3"
```

And used in this context.

```haskell

val1 = read . reverse . takeBack . reverse $ outxs :: Double
val2 = read . takeBack $ xs :: Double

```

From 2 diferent sources.

Because remember when it does not match the operator `+` or `-`, it just constructs `outxs` with the `Char` it finds.

```haskell

| otherwise = subProtoCalc xs (outxs ++ [x])

```

But when it matches,  it just takes the first value, so the one already found in `outxs` and since it appended it, it must `reverse` it first and then input it in `takeBack`.

Because it used `val1` for the computation, then this value must be removed from `outxs`.

```haskell

newoutxs = reverse . takeTailN . reverse $ outxs

```

With:

```haskell

takeTailN :: [Char] -> [Char]
takeTailN [] = []
takeTailN (x:xs)
    | not (x `elem` "+-*/") = takeTailN xs
    | otherwise = x:xs

```

Same thing for `newxs`, because `val2` has been used.

```haskell

newxs = takeTailN xs

```

And we replace `val1` in `outxs` by the result for next recursive call.

```haskell

subProtoCalc2 newxs (newoutxs ++ (show (val1 + val2))) (n + 1)

```

Same logic when `val1` is a negative, but we must adapt the result.

To check if `val1` is negative, now we just check the last value of `newoutxs` the penultimate value of `outxs`.

```haskell

else if last newoutxs /= '-'

```

And we adapt in consequences.

```haskell

else if val1 > val2
     then subProtoCalc2 newxs (newoutxs ++ (show (val1 - val2))) (n + 1)
     else subProtoCalc2 newxs (init newoutxs ++ (show (val2 - val1))) (n + 1)

```

That's all for `subProtoCalc2`.

Btw, note that we could simplify the handle of negative values by just using this function instead of naive `takeBack`.

```haskell

takeBack2 :: [Char] -> Int -> [Char]
takeBack2 [] _ = []
takeBack2 (x:xs) n 
    | not (x `elem` "+-*/") = (x:takeBack2 xs (n+1))
    | otherwise = if n == 0 then (x:takeBack2 xs (n+1)) else []

```

Because here we consider that `'-'` as first `Char` is not an operator but part of the value.

Then it is in `val1` or `val2` and wors well directly with `read`.

```haskell

ghci> read "-6" :: Double
-6.0

```

But the current impl uses the complicated and ineleguant negative handling...

Fell free to improove it.

We could do a same variant for `takeTailN`.

## Execution model

Do you know where `subprotoCalc2` lives in the model ?

For now i can not tell you a clear view of the model but i want you to understand that is must executes just after `subProtocalc1` which does the same thing than `subProtocalc2` but with `*` and `/`. 

That is totaly normal, because they are prioritary operators.

Here it is.

```haskell

subProtoCalc :: [Char] -> [Char] -> [Char]
subProtoCalc [] outxs = outxs
subProtoCalc (x:xs) outxs
    | x == '*' = 
        if head xs /= '-'
        then let val1 = read . reverse . takeBack . reverse $ outxs :: Double
                 val2 = read . takeBack $ xs :: Double
                 newoutxs = reverse . takeTailN . reverse $ outxs
                 newxs = takeTailN xs
             in subProtoCalc newxs (newoutxs ++ (show (val1 * val2)))
        else let xsb = tail xs
                 val1 = read . reverse . takeBack . reverse $ outxs :: Double
                 val2 = read . takeBack $ xsb :: Double
                 newoutxs = reverse . takeTailN . reverse $ outxs
                 newxs = takeTailN xsb
             in  if null newoutxs
                 then subProtoCalc newxs (newoutxs ++ (show (-val1 * val2)))
                 else if last newoutxs /= '-'
                     then subProtoCalc newxs (init newoutxs ++ (show (-val1 * val2)))
                     else subProtoCalc newxs (init newoutxs ++ "+" ++ (show (val1 * val2)))
    | x == '/' = 
        if head xs /= '-'
        then let val1 = read . reverse . takeBack . reverse $ outxs :: Double
                 val2 = read . takeBack $ xs :: Double
                 newoutxs = reverse . takeTailN . reverse $ outxs
                 newxs = takeTailN xs
             in subProtoCalc newxs (newoutxs ++ (show (val1 / val2)))
        else let xsb = tail xs
                 val1 = read . reverse . takeBack . reverse $ outxs :: Double
                 val2 = read . takeBack $ xsb :: Double
                 newoutxs = reverse . takeTailN . reverse $ outxs
                 newxs = takeTailN xsb
             in if null newoutxs
                then subProtoCalc newxs (newoutxs ++ (show (-val1 / val2)))
                else if last newoutxs /= '-'
                    then subProtoCalc newxs (init newoutxs ++ (show (-val1 / val2)))
                    else subProtoCalc newxs (init newoutxs ++ "+" ++ (show (val1 / val2)))
    | otherwise = subProtoCalc xs (outxs ++ [x])

```

Note that it follows the same structure than `subProtoCalc2` btut does not need to check if `-` is an operator or just describing the value because it just cares about `*` and `/`.

Here is `protoCalc`, see the execution model respecting PEMDAS ?

```haskell

protoCalc :: [Char] -> [Char]
protoCalc xs = 
    let outxs = subProtoCalc2 (subProtoCalc xs []) [] 0
    in outxs

```

In fact 



