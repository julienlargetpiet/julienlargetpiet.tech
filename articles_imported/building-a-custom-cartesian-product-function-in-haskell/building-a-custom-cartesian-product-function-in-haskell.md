
In this article we'll explore the implementation of the cartesian product of `m` elements of `n` lists.

Look at this Haskell example:

```haskell

ghci> sequence [[1, 2], [3, 4, 5]]
[[1,3],[1,4],[1,5],[2,3],[2,4],[2,5]]

```

That's something we take for granted in high abstraction level languages such as Haskell or Python, or even in high abstraction libs for low-level languages (i do not have example sorry).

To begin with, we will explore my very first attempt at implementing this function in haskell.

We will benchmarks performance in term of computation speed and memory footprint between the different architectures i implemented for this function.

After that, we will go over C and, yet again try different architectures.

Spoiler, one architecture is roughly **9 times quicker** and allocates 3 times less bytes.

## Naive architecture

This is the implementation you do when you are not yet fully familiarized with functional programming.

You dispatch responsabilities between different functions, implements ti in a very C way but must match the Haskell synthax.

It is like fightng Haskell to try do implement something performant.

No surprise, it led to the worst result.

But still interesting implementation, because this is the fundations for the next ones.

### Fundational functions

We begin with:

```haskell

subMySequence :: Int -> [Int] -> Int -> [Int]
subMySequence _ [] _ = []
subMySequence idx (x:xs) n = if idx /= n
                             then x:(subMySequence idx xs (n + 1))
                             else (x + 1):(subMySequence idx xs (n + 1))

subMySequence2 :: Int -> [Int] -> Int -> [Int]
subMySequence2 _ [] _ = []
subMySequence2 idx (x:xs) n = if idx /= n
                              then x:(subMySequence2 idx xs (n + 1))
                              else (-1):(subMySequence2 idx xs (n + 1))

subMySequence3 :: Int -> [Int] -> Int -> [Int]
subMySequence3 _ [] _ = []
subMySequence3 idx (x:xs) n = if idx /= n
                              then x:(subMySequence3 idx xs (n + 1))
                              else 0:(subMySequence3 idx xs (n + 1))

```

Hmm, ok.

They kind of do the same thing, take 2 `Int` and a list of `Int`.

The first int is called `idx` and is the one that must be checked at each iteration (recursive function call) with the incrementer `n` (second `Int`).

When they are the same value, we either:

- `mySequence` -> increment by one the associated value at the same index

- `mySequence2` -> set to `-1` the associated value at the same index

- `mySequence3` -> set to `0` the associated value at the same index


**"Why the hell do we do that ?"**

### Architecture

Because, look at where they are used:

```haskell

mySequenceIdsn :: [Int] -> [Int] -> Int -> [[Int]]
mySequenceIdsn lxs ids idx
    | idx == 0 = if val == (cmp - 1)
                 then []
                 else let newids = subMySequence 0 ids 0
                          newids2 = subMySequence2 (length lxs - 1) newids 0
                      in mySequenceIdsn lxs newids2 (length lxs - 1)
    | val < cmp - 1 = 
        let newids = subMySequence idx ids 0
        in  newids:(mySequenceIdsn lxs newids (length lxs - 1))
    | otherwise = 
        let newids = subMySequence3 idx ids 0
        in  mySequenceIdsn lxs newids (idx - 1)
    where val = (ids !! idx)
          cmp = (lxs !! idx)

```

Wow, a A LOT of work there.

So first, what is the function intent ?

It has to generate all set of indices that will be used for building all the cartesian products. (separation of concerns)

Like that, indices could be reused without recomputing it for generating another cartesiaj product with the same dimensions.

AnotherReconsider the previou example:

```haskell

ghci> sequence [[1, 2], [3, 4, 5]]
[[1,3],[1,4],[1,5],[2,3],[2,4],[2,5]]

```

Here i have a cartesian product with dimensions `2, 3`, yep each value is the length of each list.

Now, what can be said abut that ?

We can think of a way to represent this cartesian product as a list of pairs containing the indices of each element for the associated list right ?

So we can for instance encode the first product of the cartesian product which is `[1, 3]` as a pair of the first index of te first list and the first index of the second list, hence -> `[0, 0]`.

So the whole structure is:

```haskell

[[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]]

```

And then there will be a function taht will take the data that is in the example `[[1, 2], [3, 4, 5]]` and take the values sequenctialy with the generated indices so it generate the result.

This is a very nice separation of concerns because here, the indices are reusable for another data input that has the same dimensions, so no need for expansive recomputation and allocation.

But going back to the function, what was going on ?

First we do that:

```haskell

where val = (ids !! idx)
      cmp = (lxs !! idx)


```

It means, `val` is the actual value of the index

And...

`cmp` is the dimension associated to the list of the index.

Because `lxs` comes from.

```haskell

mySequencePrepareLength :: [[a]] -> [Int]
mySequencePrepareLength [] = []
mySequencePrepareLength (x:xs) = (length x):(mySequencePrepareLength xs)

```

That just set the dimension in a list for the current data.

Example

```haskell

ghci> mySequencePrepareLength [[1, 2], [3, 4, 5]]
ghci> [2,3]

```

Now, there is only 3 posibilities:

- `idx == 0` -> Nop, because we start at `idx = length (data - 1)`, the last index 

- `val < cmp - 1` -> Yess

Why ?

Because at the very start ids is just `[0, -1]`, given by this function:

```haskell

mySequencePrepareIds :: [[a]] -> [Int]
mySequencePrepareIds [_] = (-1):[]
mySequencePrepareIds (_:xs) = 0:(mySequencePrepareIds xs)

```

Wo what we do is just increment the `-1` to `0` with `subMySequence idx ids 0`.

And, bomm, we got our first index pairs -> `[0, 0]`.

So we just append it in the result:

```haskell

in  newids:(mySequenceIdsn lxs newids (length lxs - 1))

```

We repeat that until the index go outside of the dimension / length fo the current list related to this `idx`.

So, at this point this function is taken.

```haskell

| otherwise = 
    let newids = subMySequence3 idx ids 0
    in  mySequenceIdsn lxs newids (idx - 1)

```

"What do we do there ?"

We just set `0` back to the value of the current index and decrement by one the index for the next calls, so we wil increment the previous index.

In the example, that is literally the step from:

```haskell

[0, 2]

```

to 

```haskell

[1, 0]

```

At some point the `idx` will be equal to `0`.

This function will be taken:

```haskell

| idx == 0 = if val == (cmp - 1)
    then [] -- finish
    else let newids = subMySequence 0 ids 0
             newids2 = subMySequence2 (length lxs - 1) newids 0
         in mySequenceIdsn lxs newids2 (length lxs - 1)

```

As you see we know that we are finished when `idx == 0` (the end) and its value is at the maximum the dimension/length of the related list allow.

If we are not at the last value possible for the index, then we just increment it by 1 and go back to the last index.

Here is the full code:

```haskell

import Control.DeepSeq (deepseq)

mySequence :: [[a]] -> [[a]]
mySequence xs = 
    let lxs = mySequencePrepareLength xs
        ids = mySequencePrepareIds xs
    in [mySequenceList xs lids | lids <- mySequenceIdsn lxs ids l]
    where l = length xs - 1

mySequenceList :: [[a]] -> [Int] -> [a]
mySequenceList _ [] = []
mySequenceList [] _ = []
mySequenceList (x:xs) (idx:ids) = (x !! idx):(mySequenceList xs ids)

mySequencePrepareLength :: [[a]] -> [Int]
mySequencePrepareLength [] = []
mySequencePrepareLength (x:xs) = (length x):(mySequencePrepareLength xs)

mySequencePrepareIds :: [[a]] -> [Int]
mySequencePrepareIds [_] = (-1):[]
mySequencePrepareIds (_:xs) = 0:(mySequencePrepareIds xs)

mySequenceIdsn :: [Int] -> [Int] -> Int -> [[Int]]
mySequenceIdsn lxs ids idx
    | idx == 0 = if val == (cmp - 1)
                 then []
                 else let newids = subMySequence 0 ids 0
                          newids2 = subMySequence2 (length lxs - 1) newids 0
                      in mySequenceIdsn lxs newids2 (length lxs - 1)
    | val < cmp - 1 = 
        let newids = subMySequence idx ids 0
        in  newids:(mySequenceIdsn lxs newids (length lxs - 1))
    | otherwise = 
        let newids = subMySequence3 idx ids 0
        in  mySequenceIdsn lxs newids (idx - 1)
    where val = (ids !! idx)
          cmp = (lxs !! idx)

subMySequence :: Int -> [Int] -> Int -> [Int]
subMySequence _ [] _ = []
subMySequence idx (x:xs) n = if idx /= n
                             then x:(subMySequence idx xs (n + 1))
                             else (x + 1):(subMySequence idx xs (n + 1))

subMySequence2 :: Int -> [Int] -> Int -> [Int]
subMySequence2 _ [] _ = []
subMySequence2 idx (x:xs) n = if idx /= n
                              then x:(subMySequence2 idx xs (n + 1))
                              else (-1):(subMySequence2 idx xs (n + 1))

subMySequence3 :: Int -> [Int] -> Int -> [Int]
subMySequence3 _ [] _ = []
subMySequence3 idx (x:xs) n = if idx /= n
                              then x:(subMySequence3 idx xs (n + 1))
                              else 0:(subMySequence3 idx xs (n + 1))

```

And we repeat this process.

It works great, produces good result.

But is it actualy efficient ?

### Benchmarks

```haskell


benchmarkSequenceNative :: [[Int]] -> Int -> Int
benchmarkSequenceNative xs 1 =
    let r = sequence xs
    in r `deepseq` length r
benchmarkSequenceNative xs n =
    let r = sequence xs
    in r `deepseq` benchmarkSequenceNative xs (n - 1)

main :: IO ()
main =
    let inpt =
            [ [0,  1,  2,  3,  4]  
            , [10, 11, 12, 13, 14] 
            , [20, 21, 22, 23, 24] 
            , [30, 31, 32, 33, 34] 
            , [40, 41, 42, 43, 44] 
            ]
        iter = 100000
    in print $ benchmarkSequence1 inpt iter

```

The dimensions is actually `5^5` which makes `3125` different combinations.

We use `deepseq`, if you do not know why, just check [https://julienlargetpiet.tech/articles/why-parsers-were-invented.html#seq-the-one-that-forces-evaluation](https://julienlargetpiet.tech/articles/why-parsers-were-invented.html#seq-the-one-that-forces-evaluation)

Now, we compile.

See [https://julienlargetpiet.tech/articles/why-parsers-were-invented.html#back-to-benchmarks](https://julienlargetpiet.tech/articles/why-parsers-were-invented.html#back-to-benchmarks) for details about flags.

```bash

ghc -O2 -rtsopts sequence.hs -o sequence

```

And run it:

```bash

./sequence +RTs -s

```

Results:

```

3125
 192,734,450,784 bytes allocated in the heap
   3,651,494,352 bytes copied during GC
          99,280 bytes maximum residency (2 sample(s))
          29,400 bytes maximum slop
               6 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0     46450 colls,     0 par    1.163s   1.184s     0.0000s    0.0002s
  Gen  1         2 colls,     0 par    0.000s   0.000s     0.0002s    0.0003s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time   29.321s  ( 29.298s elapsed)
  GC      time    1.163s  (  1.184s elapsed)
  EXIT    time    0.000s  (  0.008s elapsed)
  Total   time   30.484s  ( 30.490s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    6,573,271,381 bytes per MUT second

  Productivity  96.2% of total user, 96.1% of total elapsed

```

Lol, **192.7GB allocated over the time**.

Garbage Collector optimized that to 3.6GB.

And it took **30.490s**.

Absolute CINEMA.

## More Haskellish architecture

This implementation is legit smart, taking advantages of compregenssion lists abstraction.

Example.

```haskel

ghci> [[a, b] | a <- [1, 2], b <- [3, 4, 5]]
[[1,3],[1,4],[1,5],[2,3],[2,4],[2,5]]

```

Yess, they are the same!

Literally:

```haskell

ghci> [[a, b] | a <- [1, 2], b <- [3, 4, 5]] == sequence [[1, 2], [3, 4, 5]]
True

```

Then we just literally **extend** the inputs (2 lists here), to `n` list with expansion (recursive call with list tail.

```haskell

mySequence2 :: [[a]] -> [[a]]
mySequence2 [] = [[]]
mySequence2 (xs:xss) = [x:ys | x <- xs, ys <- mySequence2 xss]

```

Literally an expansion to `[[...] | x1 <- [...], x2 <- [...]...]`.

### Benchmarks

Now, it's time to perform benchmarks (`-O2` etcetera).

```haskell

benchmarkSequence2 :: [[Int]] -> Int -> Int
benchmarkSequence2 xs 1 =
    let r = mySequence2 xs
    in r `deepseq` length r
benchmarkSequence2 xs n =
    let r = mySequence2 xs
    in r `deepseq` benchmarkSequence2 xs (n - 1)

main :: IO ()
main =
    let inpt =
            [ [0,  1,  2,  3,  4]  
            , [10, 11, 12, 13, 14] 
            , [20, 21, 22, 23, 24] 
            , [30, 31, 32, 33, 34] 
            , [40, 41, 42, 43, 44] 
            ]
        iter = 100000
    in print $ benchmarkSequence2 inpt iter

```

Straight to results.

```

❯ ./sequence +RTS -s
3125
  31,392,050,784 bytes allocated in the heap
     215,335,000 bytes copied during GC
          62,008 bytes maximum residency (2 sample(s))
          29,400 bytes maximum slop
               6 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0      7518 colls,     0 par    0.103s   0.106s     0.0000s    0.0001s
  Gen  1         2 colls,     0 par    0.000s   0.000s     0.0002s    0.0003s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time    4.698s  (  4.695s elapsed)
  GC      time    0.104s  (  0.107s elapsed)
  EXIT    time    0.000s  (  0.009s elapsed)
  Total   time    4.802s  (  4.810s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    6,681,887,428 bytes per MUT second

```

Woo, a massive performance jump !

From hamf a minute to `4.8` seconds.

And from pratically `200GB` of memory allocations to `31.4GB`.

Not too bad, especialy considering native `sequence`

## Native implementation

### Benchmarks

```haskell

benchmarkSequenceNative :: [[Int]] -> Int -> Int
benchmarkSequenceNative xs 1 =
    let r = sequence xs
    in r `deepseq` length r
benchmarkSequenceNative xs n =
    let r = sequence xs
    in r `deepseq` benchmarkSequenceNative xs (n - 1)

main :: IO ()
main =
    let inpt =
            [ [0,  1,  2,  3,  4]  
            , [10, 11, 12, 13, 14] 
            , [20, 21, 22, 23, 24] 
            , [30, 31, 32, 33, 34] 
            , [40, 41, 42, 43, 44] 
            ]
        iter = 100000
    in print $ benchmarkSequenceNative inpt iter

```

Straight to the results (`-O2` etcetera).

```

❯ ./sequence +RTS -s
3125
  31,392,050,784 bytes allocated in the heap
     215,335,000 bytes copied during GC
          62,008 bytes maximum residency (2 sample(s))
          29,400 bytes maximum slop
               6 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0      7518 colls,     0 par    0.101s   0.104s     0.0000s    0.0001s
  Gen  1         2 colls,     0 par    0.000s   0.000s     0.0002s    0.0003s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time    4.320s  (  4.316s elapsed)
  GC      time    0.102s  (  0.105s elapsed)
  EXIT    time    0.000s  (  0.010s elapsed)
  Total   time    4.422s  (  4.430s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    7,267,089,436 bytes per MUT second

  Productivity  97.7% of total user, 97.4% of total elapsed

```

Lol, so it looks we just discovered the Haskell implementation of `sequence`, praticaly the exact same results.

## Changing Data Represntation

At this point, we can suppose the bottleneck is the representation of the results which are `[[a]]`, where `a` is the atomic type.

Because in Haskell, lists are linked List.

Basically:

```haskell

data List a
    = Empty
    | Cons a (List a)

```

So we maybe need to change the reprensentation to contiguous vector to make it more performant ??

That's exactly what we'll do.

We'll use this ones:

```haskell

import qualified Data.Vector.Unboxed as U
import qualified Data.Vector as B
import qualified Data.Vector.Unboxed.Mutable as M

```













