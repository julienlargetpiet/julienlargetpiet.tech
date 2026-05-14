
In this article, we’ll explore something that looks innocent: computing the cartesian product of several lists.

In Haskell, it is almost boring:

```haskell

ghci> sequence [[1, 2], [3, 4, 5]]
[[1,3],[1,4],[1,5],[2,3],[2,4],[2,5]]

```

Clean, elegant, one function call.

And that is exactly why it is interesting.

High-level languages let us treat this kind of operation as obvious. We call `sequence`, or `itertools.product` (Python), and move on with our lives. But under the abstraction, there is still a real data structure being built, memory being allocated, indices being advanced, values being copied, and eventually a CPU doing the dirty work.

So I wanted to take this simple operation and push it through several implementations.

First, we’ll start with my first Haskell attempt: not idiomatic, a bit painful, and honestly quite funny in retrospect. Then we’ll move toward a cleaner Haskell version, compare it with native sequence, and change the data representation with vectors (native Haskell lists are in fact linked lists).

After that, we’ll leave Haskell poetry behind and go into C violence: manual allocation, fused loops, and heaptrack.

The real question is:

How much does representation and architecture matter?

Spoiler: a lot.

In the best case, one architecture ends up roughly 2 times faster than native Haskell `sequence`, and allocates about 3 times less memory.

And we haven’t even talked about the C version yet, which casually crushes native `sequence` by running roughly 9 times faster.

Before we start, if you want to reproduce the results at home (GHC Haskell compiler is assumed to be installed), you will need to install the Haskell vector package:

On debian / ubuntu based distro:

```bash

sudo apt install libghc-vector-dev

```

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

Ok, we'll describe each one.

First, the `Unboxed` vectors mean they can onlu contain atomic types, like  `Int`, `Double`, `Float`, `Bool` and `Char`.

Example:

```haskell

U.Vector Int

```

Works,but this does not.

```haskell

U.Vector (U.Vector)

```

Because they store direct values, while `B.Vector` stores reference/pointers to Haskell values.

So this works.

```haskell

B.Vector (U.Vector)

```

Now, the difference between `M` and `U` is basically that we can write into `M` vectors and `U` are immutables - read-only.

But, note that the `M` are mutable only in `runST` context.

So this works:

```haskell

import Control.Monad.ST
import qualified Data.Vector.Unboxed as U
import qualified Data.Vector.Unboxed.Mutable as M

makeVec :: U.Vector Int
makeVec = runST $ do
    mv <- M.new 3

    M.write mv 0 10
    M.write mv 1 20
    M.write mv 2 30

    U.unsafeFreeze mv

```

### What is `runST` ?

`runST` is the thing that lets you do local mutation in Haskell while keeping the outside function pure.

It is like a `let` that creates a private local world where mutation is allowed.

A normal let:

```haskell

let x = 10
    y = x + 1
in y

```

means:

- create local names
- compute result
- only result escapes

runST:

```haskell

runST $ do
    mv <- M.new 3
    M.write mv 0 10
    M.write mv 1 20
    M.write mv 2 30
    U.freeze mv

```

means:

- create local mutable things
- mutate them
- return final immutable result
- only result escapes

So the analogy is:

- let -> local pure bindings

- runST -> local mutable state

But there is one big difference: `let` is pure and lazy, while `runST` sequences operations.

With `let`, order is not really the point:

```haskell

let a = 1 + 2
    b = 3 + 4
in a + b

```

Haskell can evaluate `a` and `b` when needed.

With `runST`, order matters:

```haskell

runST $ do
    M.write mv 0 10
    M.write mv 0 20
    M.read mv 0

```

This returns `20`, because the writes happen in order.

`ST` means `State Thread`.

The type is roughly:

```haskell

runST :: (forall s. ST s a) -> a

```

The important part is this mysterious `s`.

```haskell

ST s a

```

means:

A computation that can mutate state belonging to the private state thread `s`, and finally returns an `a`.

So the whole type means:

Give me an `ST` computation that works for any possible private state token `s`, and I will return the pure result `a`.

Inside one `runST`, all the mutable things and operations share the same state-thread tag `s`.

The `s` is a fake type-level token used by the compiler to make sure mutable references/vectors cannot escape.

Example:

```haskell

makeVec :: U.Vector Int
makeVec = runST $ do
    mv <- M.new 3
    M.write mv 0 42
    U.freeze mv

```

This is allowed because the mutable vector `mv` stays inside `runST`.

"But is that alowed ?"

```haskell

makeVec :: M.MVector Int 
makeVec = runST $ do 
    mv <- M.new 3 
    M.write mv 0 42 
    mv

```

No, that is not allowed, and this is exactly the safety point of `runST`.

Haskell will reject it, because `mv` is mutable and depends on the private `s`. 

Returning it would let the mutable vector escape outside `runST`.

The compiler basically says:

Nope, this mutable vector belongs to the private `ST` world.

You cannot return it outside.

What is allowed is freezing it first:

```haskell

import Control.Monad.ST
import qualified Data.Vector.Unboxed as U
import qualified Data.Vector.Unboxed.Mutable as M

makeVec :: U.Vector Int
makeVec = runST $ do
    mv <- M.new 3
    M.write mv 0 42
    U.unsafeFreeze mv

```

Now the returned value is immutable:

```haskell

U.Vector Int

```

So it can safely escape.

The core rule:

- Mutable vector:   `M.MVector s Int`  -> cannot escape `runST`

- Immutable vector: `U.Vector Int`     -> can escape `runST`

Also, inside the `do` block, the last line must be an action. So this:

```haskell

mv

```

is not enough. You would write:

```haskell

pure mv

```

But even then, `runST` rejects it because of the escaping `s`.

So the valid pattern is:

```haskell

runST $ do
    mv <- M.new n
    -- mutate mv
    U.freeze mv

```

Or faster, when you promise not to mutate after:

```haskell

runST $ do
    mv <- M.new n
    -- mutate mv
    U.unsafeFreeze mv

```

### The Indices

We have to implement a function that will compute the **number of combinations**.

```haskell

totalLength :: U.Vector Int -> Maybe Int
totalLength lengths =
    U.foldM' step 1 lengths
  where
    step acc x
      | x == 0 = Just 0
      | acc > maxBound `div` x = Nothing 
      | otherwise = Just (acc * x)

```

Not, that to avoid `Int` (on 64bits system, they are `64bits` long) overflow, we apply this check:

```haskell

| acc > maxBound `div` x = Nothing 

```

Btw, this does not works:

```haskell

ghci> maxBound `div` 2

```

--> Error

Because it has not enough context, like maximum bound of what types?

It is normally .

```haskell

ghci> (maxBound :: Int) `div` 2
4611686018427387903

```

Or

```haskell

ghci> maxBound `div` (2 :: Int)
4611686018427387903

```

That works -> When at least one input value type is known.

So why does `totalLength` work ?

Because in he fold function, the fold function beeing `step` and the accumulator beeing `1`.

But again `1` of what type.

That is there that the type inference comes in, because we know that each value the `acc` will be multiplied with in there:

```haskell

| otherwise = Just (acc * x)

```

Is with an `Int`, because `x` is an element from `lengths`:

```haskell

U.foldM' step 1 lengths

```

So `acc` must be an `Int`.

There 

It is like that:

```haskell

ghci> maxBound `div` (2 :: Int)
4611686018427387903

```

But, now the big boy generating the pairs of indices !

```haskell

cartesianIndices :: U.Vector Int -> U.Vector Int
cartesianIndices lengths = runST $ do
    let !ndim = U.length lengths

    case totalLength lengths of
      Nothing -> error "cartesianIndices: total size overflow"
      Just 0  -> U.unsafeFreeze =<< M.new 0 
      Just total -> do
          out <- M.unsafeNew (total * ndim) 
          cur <- M.replicate ndim 0 
          let loop row
                | row >= total = pure () 
                | otherwise = do
                    let !rowIdx = row * ndim 
                    forM_ [0 .. ndim - 1] $ \i -> do
                        v <- M.unsafeRead cur i
                        M.unsafeWrite out (rowIdx + i) v

                    let carry dim
                          | dim < 0 = pure ()
                          | otherwise = do
                              v <- M.unsafeRead cur dim
                              let limit = U.unsafeIndex lengths dim 

                              if v == limit - 1
                              then do
                                M.unsafeWrite cur dim 0
                                carry (dim - 1)
                              else do
                                M.unsafeWrite cur dim (v + 1)

                    carry (ndim - 1)
                    loop (row + 1)

          loop 0
          U.unsafeFreeze out

```

So, generating the returned vector:

```haskell

out <- M.unsafeNew (total * ndim) 

```

It is a flat Mutable one, length is **number of combinations X dimensions**.

After, that, this is standard loops, with current vector that will encode all the index for a particular combinations of indices:

```haskell

cur <- M.replicate ndim 0 

```

(whose first all values are set to `0`)

But wait just a little thing before diving into the algorithmic.

A brief type analysis.

Why the `loop` function, at some point returns `pure ()` ?

```haskell

let loop row
      | row >= total = pure () 
      | otherwise = do
          let !rowIdx = row * ndim --OUT0
          forM_ [0 .. ndim - 1] $ \i -> do
              v <- M.unsafeRead cur i
              M.unsafeWrite out (rowIdx + i) v --OUT1

          let carry dim
                | dim < 0 = pure ()
                | otherwise = do
                    v <- M.unsafeRead cur dim
                    let limit = U.unsafeIndex lengths dim 

                    if v == limit - 1
                    then do
                      M.unsafeWrite cur dim 0 -- OUT2
                      carry (dim - 1)
                    else do
                      M.unsafeWrite cur dim (v + 1) -- OUT3

          carry (ndim - 1)
          loop (row + 1)

```

Because, you see that all the others output branches returns a write action on a mutable vector `M.unsafeWrite`.

And its signature inside the `runST` context is:

```haskell

M.unsafeWrite :: M.MVector s Int -> Int -> Int -> ST s ()

```

So, in the path where we have nothing to do, we just return an empty `ST` action with `pure ()`.

Because its signature is:

```haskell

pure :: Applicative f => a -> f a

```

So, in `ST`:

```haskell

pure :: a -> ST s a
pure () = ST s ()

```

`()` is the unit value.

It is not an empty variable. It is a real value, but it carries no information.

In Haskell there is a type also called `()`:

```haskell

() :: ()

```

This looks weird because the type and the only value of that type have the same spelling.

Think of it like this:


```haskell

Bool

```

has two values:

```haskell

True
False

```

But:


```

()

```


has exactly one value:

```

()

```

So:

```haskell

() :: ()

```

means:

the value `()` has type `()`.

It is used when you want to say: “there is no meaningful result here.”

For example:

```haskell

putStrLn :: String -> IO ()

```

`putStrLn` does something: it prints text. But it does not produce a useful result after printing. So its result type is:

```haskell

IO ()

```

Meaning:

an `IO` action that, when executed, returns no interesting value.

Same with mutable vector writes:

```haskell

M.unsafeWrite :: M.MVector s a -> Int -> a -> ST s ()

```

Writing into a vector changes memory, but the returned value is not interesting. So it returns:

```

ST s ()

```

Meaning:

An `ST` action that mutates something and returns no useful value.

But now, let's dissect the algo.

So we got a temprorary `ndim` length mutable vector that carries the current indices combination for a combination which is `cur`.

When one combination is found, we copy it at the right place with:

```haskell

let !rowIdx = row * ndim 
forM_ [0 .. ndim - 1] $ \i -> do
    v <- M.unsafeRead cur i
    M.unsafeWrite out (rowIdx + i) v

```

Note, you see this `!` ?

It if for telling Haskell to evaluate this expression and not hold it in a memory space until it need to be evaluated, in this context here:

```haskell

rowIdx + i

```

(first iteration)

So we compute the value of `rowIdx` directly.

You also need to put that as the very first line of the haskell code:

```haskell

{-# LANGUAGE BangPatterns #-}

```

And what do we do to find the current indices combination ?

We do:

```haskell

let carry dim
      | dim < 0 = pure ()
      | otherwise = do
          v <- M.unsafeRead cur dim
          let limit = U.unsafeIndex lengths dim 

          if v == limit - 1
          then do
            M.unsafeWrite cur dim 0
            carry (dim - 1)
          else do
            M.unsafeWrite cur dim (v + 1)

```

Starting at the last index (like the first version):

```haskell

carry (ndim - 1)

```

In fact, that is exactly the same logic as the first implementation, just applied to vectors.

Why the use of **unsafe** operations.

Because, it is fatser by not checking if we read or write in the curretn memory of the vector.

Example:

```haskell

ghci> set -package vector
package flags have changed, resetting and loading new packages...
ghci> import qualified Data.Vector.Unboxed.Mutable as M
ghci> m <- M.new 2 :: IO (M.IOVector Int)

```

Then when i read:

```haskell

ghci> M.read m 0
0

```

As intended.

But, when i read out of bounds.

```haskell

ghci> M.read m 2

```

-> Error

But, when i use `M.unsafeRead`, no problem, just unsafe value.

```haskell

ghci> M.unsafeRead m 2
125646898259200

```

Same for write.

```haskell

ghci> M.write m 0 44
ghci> M.read m 0
44

```

And, error when writing value out of bounds.

```haskell

ghci> M.write m 2 44

```

-> Error

But using `unsafe` varian:

```haskell

ghci> M.unsafeWrite m 2 44
ghci> M.unsafeRead m 2
44

```

That works.

And of course, we can store value of read operations.

```haskell

ghci> x = M.unsafeRead m 0
ghci> x
44

```

And we do that until we find all the indices combinations:

```haskell

loop (row + 1)

```

With the stop being, as discussed earlier:

```haskell

| row >= total = pure () 

```

Because the return type of `cartesianIndices` should be a vector that has no reason to be muted (`U.Vector Int`), so we convert the `M.Vector Int` to it:

```haskell

U.unsafeFreeze out

```

What is the difference between `U.unsafeFreeze` and `U.freeze` ?

The difference is copy vs no copy.

With mutable vectors:

```haskell

import qualified Data.Vector.Unboxed as U
import qualified Data.Vector.Unboxed.Mutable as M

```

You have:

```haskell

U.freeze       :: M.MVector s a -> ST s (U.Vector a)
U.unsafeFreeze :: M.MVector s a -> ST s (U.Vector a)

```

or in `IO`:

```haskell

U.freeze       :: M.IOVector a -> IO (U.Vector a)
U.unsafeFreeze :: M.IOVector a -> IO (U.Vector a)
```

Hence, 

```haskell

U.freeze
U.freeze mv

```

makes an immutable copy of the mutable vector.

So after:

```haskell

v <- U.freeze mv

```

you can still mutate `mv`, and `v` stays unchanged.

Example idea:

```haskell

mv <- M.new 2 :: IO (M.IOVector Int)

M.write mv 0 10
M.write mv 1 20

v <- U.freeze mv

M.write mv 0 999

print v

```

`v` is still:

```

[10,20]

```

because `freeze` copied the data.

```haskell

U.unsafeFreeze
U.unsafeFreeze mv

```

does not copy. It reuses the same memory and gives you an immutable vector view over it.

So it is **faster** -> O(1). (metadata changes)

instead of copying all elements:

O(n)

But it is called unsafe because after doing:

```haskell

v <- U.unsafeFreeze mv

```

you must not mutate mv anymore.

Because `v` and `mv` may share the same underlying memory.

Example of bad code:

```haskell

mv <- M.new 2 :: IO (M.IOVector Int)

M.write mv 0 10
M.write mv 1 20

v <- U.unsafeFreeze mv

M.write mv 0 999  -- dangerous / logically invalid

print v

```

Now `v` may appear changed too:

```

[999,20]

```

Which breaks the idea that `U.Vector` is immutable.

### The underlying data

First, we define our own data structure that is a Matrix storing data in a flat vector `U` (for access performance reason).

```haskell

data Matrix a = Matrix
  { nRows :: !Int
  , nCols :: !Int
  , values :: !(U.Vector a)
  }

unsafeIndex2D :: U.Unbox a => Matrix a -> Int -> Int -> a
unsafeIndex2D mat row col =
  U.unsafeIndex (values mat) idx
  where
    idx = row * nCols mat + col

```

So we have the best of both world, contiguous memory structure and Matrix like random access abstraction.

That is to match `[[a]]` `sequence` return type.

Here, rows are the number of combiantions and columns are just the number of lists used in the cartesian product.

Now to create the values from raw generated indices and data as `B.Vector (U.Vector Int)`.

We must define a function for that that will take these 2 inputs and generate the intended cartesian product result.

```haskell

makeMatrix :: Int -> U.Vector Int -> B.Vector (U.Vector Int) -> Matrix Int
makeMatrix !salt indices dataVec = runST $ do
    let !ndim = B.length dataVec
        !rows = U.length indices `quot` ndim
        !total = rows * ndim

    out <- M.unsafeNew total

    let loop !row
          | row >= rows = pure ()
          | otherwise = do
              let !rowIdx = row * ndim

              let inner !j
                    | j >= ndim = pure ()
                    | otherwise = do
                        let !idx = U.unsafeIndex indices (rowIdx + j)
                            !src = B.unsafeIndex dataVec j
                            !val = U.unsafeIndex src idx + salt

                        M.unsafeWrite out (rowIdx + j) val
                        inner (j + 1)

              inner 0
              loop (row + 1)

    loop 0

    frozen <- U.unsafeFreeze out

    pure Matrix
      { nRows = rows
      , nCols = ndim
      , values = frozen
      }

```

So we just create the output vector that will store all combinations result inside the matrix.

```haskell

let !ndim = B.length dataVec
    !rows = U.length indices `quot` ndim
    !total = rows * ndim

out <- M.unsafeNew total

```

And wraooed in the Matrix at the end:

```haskell

frozen <- U.unsafeFreeze out

pure Matrix
  { nRows = rows
  , nCols = ndim
  , values = frozen
  }

```

The `pure` is because it will return a `ST` application context like `runST` constext expects.

But, the crucial part is there:

```haskell

let inner !j
      | j >= ndim = pure ()
      | otherwise = do
          let !idx = U.unsafeIndex indices (rowIdx + j)
              !src = B.unsafeIndex dataVec j
              !val = U.unsafeIndex src idx + salt

          M.unsafeWrite out (rowIdx + j) val
          inner (j + 1)

```

Because it access the list of values for the current dimension.

```haskell

!src = B.unsafeIndex dataVec j

```

And access the element at the current index for this dimension, for this combination.

```haskell

!idx = U.unsafeIndex indices (rowIdx + j) -- find the associated index

```

And.

```haskell

!val = U.unsafeIndex src idx

```

Hmm, but i also add a `salt` (random value) to the value of the list in fact, so it is:


```haskell

!val = U.unsafeIndex src idx + salt

```

Why add a `salt`, we will discuss that later in the benchmark part.

**AND, i repeat this process for all combinations.**

```haskell

let loop !row
      | row >= rows = pure ()
      | otherwise = do

          ...

          inner 0
          loop (row + 1)

```

Now, let's benchmark that and se if that is better than native `sequence`.

### Benchmarks

```haskell

benchmark :: U.Vector Int -> Int -> B.Vector (U.Vector Int) -> Int
benchmark lengths iter inpt = go iter
  where
    go 1 =
        let !indices = cartesianIndices lengths
            !r = makeMatrix 1 indices inpt
        in values r `deepseq` U.length (values r)

    go n =
        let !indices = cartesianIndices lengths
            !r = makeMatrix n indices inpt
        in values r `deepseq` go (n - 1)

main :: IO ()
main = do
    let inpt1 = U.fromList [0,  1,  2,  3,  4]                   
        inpt2 = U.fromList [10, 11, 12, 13, 14]                      
        inpt3 = U.fromList [20, 21, 22, 23, 24]                      
        inpt4 = U.fromList [30, 31, 32, 33, 34]                      
        inpt5 = U.fromList [40, 41, 42, 43, 44]                       

        inpt =
                B.fromList
                  [ inpt1
                  , inpt2
                  , inpt3
                  , inpt4
                  , inpt5
                  ]

        lengths = U.fromList $ replicate 5 5

        iter = 100000

    start <- getCPUTime

    let !result = benchmark lengths iter inpt

    result `deepseq` pure ()

    end <- getCPUTime

    let elapsedNs :: Double
        elapsedNs = fromIntegral (end - start) / 1000.0 

        nsPerCall = elapsedNs / fromIntegral iter

    printf "result:      %d\n" result
    printf "iterations:  %d\n" iter
    printf "elapsed ns:  %.0f\n" elapsedNs
    printf "ns / call:   %.2f\n" nsPerCall

```

Note, that we do:

```haskell

result `deepseq` pure ()

```

Because, we are in an `IO` context, so it must return an `IO` action, and in an `IO` context, we have:

```haskell

pure :: a -> IO a
pure () :: IO ()

```

Also, let's just answer the `salt` question.

What we do in there.

```haskell

!r = makeMatrix n indices inpt

```

Where `n` is the current `tot iteration - iteration number`.

The reason is simple.

Prevent Haskell to optimize this function because the function now has always different inputs and results.

So it is not able to see that the results are always the same from al the function calls and just execute some or even one.

Even with `deepseq`, se prefere to be sure that all functions calls are executed.

Also, what is `fromItegral` from there in `main` ?

```haskell

elapsedNs = fromIntegral (end - start) / 1000.0 

```

It will just make sure that `(end - start)` can be divied by a number making it a more general numeric value than an `Int`, a `Num`.

```haskell

ghci> :t fromIntegral 3
fromIntegral 3 :: Num b => b

```

Because, here `start` and `end` are `Integer`.

```haskell

start <- getCPUTime

...

end <- getCPUTime


```

```haskell

ghci> import System.CPUTime
ghci> :t getCPUTime
getCPUTime :: IO Integer

```

So, let's see results.

```

result:      15625
iterations:  100000
elapsed ns:  5623451854
ns / call:   56234.52
  12,501,895,888 bytes allocated in the heap
          32,048 bytes copied during GC
         127,552 bytes maximum residency (2 sample(s))
          33,496 bytes maximum slop
              10 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0      2940 colls,     0 par    0.009s   0.012s     0.0000s    0.0028s
  Gen  1         2 colls,     0 par    0.002s   0.025s     0.0126s    0.0251s

  INIT    time    0.000s  (  0.002s elapsed)
  MUT     time    5.614s  (  5.621s elapsed)
  GC      time    0.011s  (  0.038s elapsed)
  EXIT    time    0.000s  (  0.000s elapsed)
  Total   time    5.625s  (  5.662s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    2,227,018,474 bytes per MUT second

  Productivity  99.8% of total user, 99.3% of total elapsed

```

Hmm, not bad but also a bit disapointing.

Sure we just cut more than in half the memory footprint.

From `30+GB` to only `12.5GB`.

But, we are stil slower than native `sequence`.

From arround `4.9s` to `5.6s`.

Not great.

But there is maybe 2 more ways we can have a chance to beat it in Haskell.

First, by a special case like this one when the dimensions of the data are the same.

Here:

```haskell

let inpt1 = U.fromList [0,  1,  2,  3,  4]                   
    inpt2 = U.fromList [10, 11, 12, 13, 14]                      
    inpt3 = U.fromList [20, 21, 22, 23, 24]                      
    inpt4 = U.fromList [30, 31, 32, 33, 34]                      
    inpt5 = U.fromList [40, 41, 42, 43, 44]                       

```

All are length `5`.

## Special case architecture

So, let's just tweak `makeMatrix`.

```haskell

makeMatrix :: Int -> Int -> U.Vector Int -> U.Vector Int -> Matrix Int
makeMatrix !salt ndim indices dataVec = runST $ do
    let !nval = U.length dataVec `quot` ndim
        !rows = U.length indices `quot` ndim
        !total = rows * ndim

    out <- M.unsafeNew total

    let loop !row
          | row >= rows = pure ()
          | otherwise = do
              let !rowIdx = row * ndim

              let inner !j
                    | j >= ndim = pure ()
                    | otherwise = do
                        let !idx = U.unsafeIndex indices (rowIdx + j)
                            !val = U.unsafeIndex dataVec (nval * j + idx) + salt

                        M.unsafeWrite out (rowIdx + j) val
                        inner (j + 1)

              inner 0
              loop (row + 1)

    loop 0

    frozen <- U.unsafeFreeze out

    pure Matrix
      { nRows = rows
      , nCols = ndim
      , values = frozen
      }


```

And call it properly.

```haskell

benchmark :: U.Vector Int -> Int -> Int -> U.Vector Int -> Int
benchmark lengths iter ndim inpt = go iter
  where
    go 1 =
        let !indices = cartesianIndices lengths
            !r = makeMatrix 1 ndim indices inpt
        in values r `deepseq` U.length (values r)

    go n =
        let !indices = cartesianIndices lengths
            !r = makeMatrix n ndim indices inpt
        in values r `deepseq` go (n - 1)

main :: IO ()
main = do
    let inpt1 = U.fromList [0,  1,  2,  3,  4]                   
        inpt2 = U.fromList [10, 11, 12, 13, 14]                      
        inpt3 = U.fromList [20, 21, 22, 23, 24]                      
        inpt4 = U.fromList [30, 31, 32, 33, 34]                      
        inpt5 = U.fromList [40, 41, 42, 43, 44]                       

        inpt =
                U.concat
                  [ inpt1
                  , inpt2
                  , inpt3
                  , inpt4
                  , inpt5
                  ]

        lengths = U.fromList $ replicate 5 5

        iter = 100000

    start <- getCPUTime

    let !result = benchmark lengths iter 5 inpt

    result `deepseq` pure ()

    end <- getCPUTime

    let elapsedNs :: Double
        elapsedNs = fromIntegral (end - start) / 1000.0 

        nsPerCall = elapsedNs / fromIntegral iter

    printf "result:      %d\n" result
    printf "iterations:  %d\n" iter
    printf "elapsed ns:  %.0f\n" elapsedNs
    printf "ns / call:   %.2f\n" nsPerCall

```

Results, please !

```

❯ ./sequence-vector3b +RTS -s
result:      15625
iterations:  100000
elapsed ns:  2498054538
ns / call:   24980.55
  12,501,895,952 bytes allocated in the heap
          31,728 bytes copied during GC
         127,112 bytes maximum residency (2 sample(s))
          33,496 bytes maximum slop
              10 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0      2940 colls,     0 par    0.008s   0.009s     0.0000s    0.0000s
  Gen  1         2 colls,     0 par    0.001s   0.001s     0.0003s    0.0004s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time    2.490s  (  2.488s elapsed)
  GC      time    0.009s  (  0.010s elapsed)
  EXIT    time    0.000s  (  0.002s elapsed)
  Total   time    2.499s  (  2.500s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    5,021,774,995 bytes per MUT second

  Productivity  99.6% of total user, 99.5% of total elapsed

```

Wow, same memory footprint, but here gentleman we beat native `sequence` !

From arround `4.5s` to `2.5s` !

## Fused Indices And underlying data

The previous architecture had the strengt to seprarate the index geenrations and the data generation.

It is great because if in a programm, we want to make the cartesian product of a lists of lists (or vectors of vectors) that share the same dimensions. 

Then, **we can just reuse the generated index to build the data which is intended tio be vastly quicker**.

But, here we just want to measure one-shot performance in cartesian product generation.

So, what if we save a huge allocations of a vector for the indices and build the data straight from the current combination ?

Looks great !

```haskell

makeMatrixDirect :: Int -> U.Vector Int -> B.Vector (U.Vector Int) -> Matrix Int
makeMatrixDirect !salt lengths dataVec = runST $ do
    let !ndim = U.length lengths

    case totalLength lengths of
      Nothing -> error "makeMatrixDirect: total size overflow"
      Just 0 ->
        pure Matrix
          { nRows = 0
          , nCols = ndim
          , values = U.empty
          }

      Just total -> do
        out <- M.unsafeNew (total * ndim)
        cur <- M.replicate ndim 0

        let loop !row
              | row >= total = pure ()
              | otherwise = do
                  let !rowIdx = row * ndim

                  let writeCols !j
                        | j >= ndim = pure ()
                        | otherwise = do
                            idx <- M.unsafeRead cur j

                            let !src = B.unsafeIndex dataVec j
                                !val = U.unsafeIndex src idx + salt

                            M.unsafeWrite out (rowIdx + j) val
                            writeCols (j + 1)

                  writeCols 0

                  let carry !dim
                        | dim < 0 = pure ()
                        | otherwise = do
                            v <- M.unsafeRead cur dim
                            let !limit = U.unsafeIndex lengths dim

                            if v == limit - 1
                              then do
                                M.unsafeWrite cur dim 0
                                carry (dim - 1)
                              else do
                                M.unsafeWrite cur dim (v + 1)

                  carry (ndim - 1)
                  loop (row + 1)

        loop 0

        frozen <- U.unsafeFreeze out

        pure Matrix
          { nRows = total
          , nCols = ndim
          , values = frozen
          }

```

After what we talked about, this is self-explanatory.

Now the benchmark !

### Benchmarks

Here, the benchmark is simplified because we build cartesian products in one function call `makeMatrixDirect`.

```haskell

benchmark :: U.Vector Int -> Int -> B.Vector (U.Vector Int) -> Int
benchmark lengths iter inpt = go iter
  where
    go 1 =
        let !r = makeMatrixDirect 1 lengths inpt
        in values r `deepseq` U.length (values r)

    go n =
        let !r = makeMatrixDirect n lengths inpt
        in values r `deepseq` go (n - 1)

```

And, `main` is basically the same:

```haskell

main :: IO ()
main = do
    let inpt1 = U.fromList [0,  1,  2,  3,  4]                    
        inpt2 = U.fromList [10, 11, 12, 13, 14]                      
        inpt3 = U.fromList [20, 21, 22, 23, 24]                      
        inpt4 = U.fromList [30, 31, 32, 33, 34]                      
        inpt5 = U.fromList [40, 41, 42, 43, 44]                       

        inpt =
                B.fromList
                  [ inpt1
                  , inpt2
                  , inpt3
                  , inpt4
                  , inpt5
                  ]

        lengths = U.fromList $ replicate 5 5

        iter = 100000

    start <- getCPUTime

    let !result = benchmark lengths iter inpt

    result `deepseq` pure ()

    end <- getCPUTime

    let elapsedNs :: Double
        elapsedNs = fromIntegral (end - start) / 1000.0 

        nsPerCall = elapsedNs / fromIntegral iter

    printf "result:      %d\n" result
    printf "iterations:  %d\n" iter
    printf "elapsed ns:  %.0f\n" elapsedNs
    printf "ns / call:   %.2f\n" nsPerCall

```

Now, the results:

```

result:      15625
iterations:  100000
elapsed ns:  6088285866
ns / call:   60882.86
  12,510,570,432 bytes allocated in the heap
          54,832 bytes copied during GC
          44,328 bytes maximum residency (1 sample(s))
          33,496 bytes maximum slop
              10 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0      2941 colls,     0 par    0.009s   0.010s     0.0000s    0.0000s
  Gen  1         1 colls,     0 par    0.000s   0.000s     0.0004s    0.0004s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time    6.079s  (  6.079s elapsed)
  GC      time    0.010s  (  0.011s elapsed)
  EXIT    time    0.000s  (  0.000s elapsed)
  Total   time    6.089s  (  6.090s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    2,057,852,667 bytes per MUT second

  Productivity  99.8% of total user, 99.8% of total elapsed

```

Crap !

We are worse than the unfused general cartesian product function !

It may be because `ghc`, the Haskell compiler has a much worst time for optimizing each of the algorithmic logic, because here all is fused in one function, so we avoid huge allocation, but at the cost of bigger complexity inside the function.

That's not dramatic neither, we keep a good memory footprint of arround `12.5GB` and we are just at `6.1s` max, compared to its unfused equivalent at arround `5.7s`.

But, there, nothing preventing us to test for the case where all dimensions of the lists are the same, like for this benchmark case !

## Special case Architecture - V2

Same logic than before, just the fused variant.

```haskell

makeMatrixDirect :: Int -> U.Vector Int -> U.Vector Int -> Matrix Int
makeMatrixDirect !salt lengths dataVec = runST $ do
    let !ndim = U.length lengths
        !nval = U.length dataVec `quot` ndim

    case totalLength lengths of
      Nothing -> error "makeMatrixDirect: total size overflow"
      Just 0 ->
        pure Matrix
          { nRows = 0
          , nCols = ndim
          , values = U.empty
          }

      Just total -> do
        out <- M.unsafeNew (total * ndim)
        cur <- M.replicate ndim 0

        let loop !row
              | row >= total = pure ()
              | otherwise = do
                  let !rowIdx = row * ndim

                  let writeCols !j
                        | j >= ndim = pure ()
                        | otherwise = do
                            idx <- M.unsafeRead cur j

                            let !val = U.unsafeIndex dataVec (nval * j + idx) + salt

                            M.unsafeWrite out (rowIdx + j) val
                            writeCols (j + 1)

                  writeCols 0

                  let carry !dim
                        | dim < 0 = pure ()
                        | otherwise = do
                            v <- M.unsafeRead cur dim
                            let !limit = U.unsafeIndex lengths dim

                            if v == limit - 1
                              then do
                                M.unsafeWrite cur dim 0
                                carry (dim - 1)
                              else do
                                M.unsafeWrite cur dim (v + 1)

                  carry (ndim - 1)
                  loop (row + 1)

        loop 0

        frozen <- U.unsafeFreeze out

        pure Matrix
          { nRows = total
          , nCols = ndim
          , values = frozen
          }

```

Now, straight to results please !

### Benchmarks

Here is the benchmark code:

```haskell

benchmark :: U.Vector Int -> Int -> U.Vector Int -> Int
benchmark lengths iter inpt = go iter
  where
    go 1 =
        let !r = makeMatrixDirect 1 lengths inpt
        in values r `deepseq` U.length (values r)

    go n =
        let !r = makeMatrixDirect n lengths inpt
        in values r `deepseq` go (n - 1)

main :: IO ()
main = do
    let inpt1 = U.fromList [0,  1,  2,  3,  4]                    
        inpt2 = U.fromList [10, 11, 12, 13, 14]                      
        inpt3 = U.fromList [20, 21, 22, 23, 24]                      
        inpt4 = U.fromList [30, 31, 32, 33, 34]                      
        inpt5 = U.fromList [40, 41, 42, 43, 44]                       

        inpt =
                U.concat
                  [ inpt1
                  , inpt2
                  , inpt3
                  , inpt4
                  , inpt5
                  ]

        lengths = U.fromList $ replicate 5 5

        iter = 100000

    start <- getCPUTime

    let !result = benchmark lengths iter inpt

    result `deepseq` pure ()

    end <- getCPUTime

    let elapsedNs :: Double
        elapsedNs = fromIntegral (end - start) / 1000.0 

        nsPerCall = elapsedNs / fromIntegral iter

    printf "result:      %d\n" result
    printf "iterations:  %d\n" iter
    printf "elapsed ns:  %.0f\n" elapsedNs
    printf "ns / call:   %.2f\n" nsPerCall


```

And the results:

```haskell

result:      15625
iterations:  100000
elapsed ns:  2446795228
ns / call:   24467.95
  12,510,570,368 bytes allocated in the heap
          54,952 bytes copied during GC
          44,328 bytes maximum residency (1 sample(s))
          33,496 bytes maximum slop
              10 MiB total memory in use (0 MB lost due to fragmentation)

                                     Tot time (elapsed)  Avg pause  Max pause
  Gen  0      2941 colls,     0 par    0.009s   0.010s     0.0000s    0.0000s
  Gen  1         1 colls,     0 par    0.000s   0.000s     0.0004s    0.0004s

  INIT    time    0.000s  (  0.000s elapsed)
  MUT     time    2.438s  (  2.437s elapsed)
  GC      time    0.009s  (  0.010s elapsed)
  EXIT    time    0.000s  (  0.003s elapsed)
  Total   time    2.448s  (  2.450s elapsed)

  %GC     time       0.0%  (0.0% elapsed)

  Alloc rate    5,130,456,844 bytes per MUT second

  Productivity  99.6% of total user, 99.5% of total elapsed

```

YESSS !

Same memory footprint and quicjer execution time !

From `2.5s` to a stable `2.460s`.

Now, what C can do ?

## The C Way Of Life (Cartesian Product)

First, the unfused version.

That will be much more straight-forward, the synthax is self-explanatory.

```C

#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <time.h>
#include <string.h>

typedef struct Matrix2D {
    size_t nrows;
    size_t ncols;
    size_t *data;
} Matrix2D;

Matrix2D matrix_create(size_t nrows, 
                       size_t ncols
                      ) {
    Matrix2D mat;

    mat.nrows = nrows;
    mat.ncols = ncols;
    mat.data = malloc(nrows * ncols * sizeof(size_t));

    if (mat.data == NULL) {
        fprintf(stderr, "Allocation failed.\n");
        exit(EXIT_FAILURE);
    }

    return mat;
}

size_t matrix_get(const Matrix2D *mat, 
                  const size_t row,
                  const size_t col) {
    return mat->data[row * mat->ncols + col];
}

bool get_total_length(
    const size_t *lengths,
    size_t ndim,
    size_t *out_total
) {
    size_t total = 1;

    for (size_t i = 0; i < ndim; ++i) {
        if (lengths[i] == 0) {
            *out_total = 0;
            return true;
        }

        if (total > SIZE_MAX / lengths[i]) {
            return false; // overflow protection
        }

        total *= lengths[i];
    }

    *out_total = total;
    return true;
}

size_t *cartesian_indices(
    const size_t *lengths,
    size_t ndim,
    size_t *out_rows
) {
    size_t total = 0;

    if (!get_total_length(lengths, ndim, &total)) {
        return NULL;
    }

    *out_rows = total;

    if (total == 0) {
        return NULL;
    }

    if (ndim == 0) {
        return NULL;
    }

    if (total > SIZE_MAX / ndim) {
        return NULL;
    }

    size_t n_elems = total * ndim;

    if (n_elems > SIZE_MAX / sizeof(size_t)) {
        return NULL;
    }

    size_t *indices = malloc(n_elems * sizeof(*indices));
    if (indices == NULL) {
        return NULL;
    }

    size_t *cur_indices = calloc(ndim, sizeof(*cur_indices));
    if (cur_indices == NULL) {
        free(indices);
        return NULL;
    }

    size_t row = 0;
    size_t dim = ndim - 1;

    while (row < total) {
        const size_t row_idx = ndim * row;

        for (size_t i = 0; i < ndim; ++i) {
            indices[row_idx + i] = cur_indices[i];
        }

        ++row;

        if (row == total) {
            break;
        }

        while (dim > 0 && cur_indices[dim] + 1 == lengths[dim]) {
            cur_indices[dim] = 0;
            --dim;
        }

        ++cur_indices[dim];
        dim = ndim - 1;
    }

    free(cur_indices);
    return indices;
}

void makeMatrix(Matrix2D *mat,
                const size_t *indices,
                const size_t *data[],
                const size_t nrows,
                const size_t ndim
               ) {

    size_t *vec = mat->data;

    for (size_t i = 0; i < nrows; ++i) {
        const size_t base_pos = i * ndim;
        for (size_t i2 = 0; i2 < ndim; ++i2) {
            vec[base_pos + i2] = data[i2][indices[base_pos + i2]];
        }
    }
}

static uint64_t now_ns(void) {
    struct timespec ts;

    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);

    return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
}


```

### Benchmarks

```C

int main(void) {

    const size_t a[] = {0,  1,  2,  3,  4};  
    const size_t b[] = {10, 11, 12, 13, 14};                         
    const size_t c[] = {20, 21, 22, 23, 24};                         
    const size_t d[] = {30, 31, 32, 33, 34};                         
    const size_t e[] = {40, 41, 42, 43, 44};                         

    const size_t *data[] = {a, b, c, d, e};

    const size_t lengths[] = {
        sizeof(a) / sizeof(a[0]),
        sizeof(b) / sizeof(b[0]),
        sizeof(c) / sizeof(c[0]),
        sizeof(d) / sizeof(d[0]),
        sizeof(e) / sizeof(e[0])
    };

    const size_t ndim = sizeof(lengths) / sizeof(lengths[0]);

    const size_t iterations = 100000;

    uint64_t start = now_ns();

    volatile size_t sink = 0;

    for (size_t i = 0; i < iterations; ++i) {
        size_t rows = 0;
        size_t *indices = cartesian_indices(lengths, ndim, &rows);

        if (indices == NULL && rows != 0) {
            fprintf(stderr, "cartesian_indices failed during benchmark\n");
            return 1;
        }

        Matrix2D mat = matrix_create(rows, ndim);
        makeMatrix(&mat, 
                   indices, 
                   data,
                   rows,
                   ndim);

        sink += mat.data[0];
        sink += mat.data[rows * ndim - 1];

        free(mat.data);
        free(indices);
    }

    uint64_t end = now_ns();

    uint64_t elapsed_ns = end - start;

    double ns_per_iter = (double)elapsed_ns / (double)iterations;

    printf("iterations:       %zu\n", iterations);
    printf("elapsed:          %" PRIu64 " ns\n", elapsed_ns);
    printf("ns / call:        %.2f\n", ns_per_iter);

    printf("sink %zu\n", sink);

    return 0;
}


```

Now, we compile with max optimizations.

```bash

❯ gcc -O3 cartesian.c -o cartesian

```

And run it.

```bash

❯ ./cartesian

```

Results.

```
❯ ./cartesian
iterations:       100000
elapsed:          1121872893 ns
ns / call:        11218.73
sink 4400000
```

Hmm, a nice `1.1s`.

The fastest we've done so far yess!

And nothing has structurally changed.

We just managed allocations manually and had a more broader control over the computation pipeline, just what C forces us to do.

So, yess very good !

But still the flat data variant to test now !

Now, we will analyze memory allocations with `heaptrack`.

```bash

sudo apt-get install heaptrack

```

```bash

❯ heaptrack ./cartesian
heaptrack output will be written to "/home/juju/99HaskellProbs/heaptrack.cartesian.52116.zst"
starting application, this might take some time...
iterations:       100000
elapsed:          1221203397 ns
ns / call:        12212.03
sink 4400000
heaptrack stats:
	allocations:          	300002
	leaked allocations:   	1
	temporary allocations:	200000
Heaptrack finished! Now run the following to investigate the data:

  heaptrack --analyze "/home/juju/99HaskellProbs/heaptrack.cartesian.52116.zst"

```

```bash

❯ heaptrack --analyze heaptrack.cartesian.52116.zst
reading file "heaptrack.cartesian.52116.zst" - please wait, this might take some time...
Debuggee command was: ./cartesian
finished reading file, now analyzing data:

MOST CALLS TO ALLOCATION FUNCTIONS
300000 calls to allocation functions with 250.00K peak consumption from
main
  in /home/juju/99HaskellProbs/cartesian
100000 calls with 125.00K peak consumption from:
100000 calls with 0B peak consumption from:
100000 calls with 125.00K peak consumption from:

...

PEAK MEMORY CONSUMERS
250.00K peak memory consumed over 300000 calls from
main
  in /home/juju/99HaskellProbs/cartesian
125.00K consumed over 100000 calls from:
125.00K consumed over 100000 calls from:

73.73K peak memory consumed over 1 calls from
0x74efaf0b738e
  in /lib/x86_64-linux-gnu/libstdc++.so.6
73.73K consumed over 1 calls from:
    call_init
      at ./elf/dl-init.c:74
      in /lib64/ld-linux-x86-64.so.2
    _dl_init::call_init
      at ./elf/dl-init.c:120
      in /lib64/ld-linux-x86-64.so.2
    _dl_init
      at ./elf/./elf/dl-init.c:121
    _dl_start_user
      in /lib64/ld-linux-x86-64.so.2

```

`250.00K` peak memory consumed over `300000` calls from `main`

Why `3000` ?

Each iteration performs three allocations:

1. `indices`

```C

size_t *indices = malloc(n_elems * sizeof(*indices));

```

That is `125K`.

2. `cur_indices`

```C

size_t *cur_indices = calloc(ndim, sizeof(*cur_indices));

```

That is tiny:

```

5 * 8 = 40 bytes

```

3. `mat.data`

```C

mat.data = malloc(nrows * ncols * sizeof(size_t));

```

That is `125K`.

So:

-> 3 allocations per iteration * 100000 iterations = 300000 allocations

That `250K` is the maximum heap memory alive at the same time.

During each iteration we allocate two big buffers:

```C

size_t *indices = malloc(n_elems * sizeof(*indices));

```

and:

```C

Matrix2D mat = matrix_create(rows, ndim);

```

Inside `matrix_create`, we allocate:

```C

mat.data = malloc(nrows * ncols * sizeof(size_t));

```

Now, benchmark dimensions are:

- `5 lists, each of length 5`

So the number of cartesian product rows is:

- `5^5 = 3125`

Each result row has:

- `5 columns`

So both the index matrix and output matrix contain:

- 3125 * 5 = 15625 values

Each value is a `size_t`, so on a 64-bit machine:

```C

sizeof(size_t) = 8 bytes

```

Therefore each big buffer is:

```

15625 * 8 = 125000 bytes

```

So:

```

indices buffer = 125000 bytes ≈ 125K
output matrix  = 125000 bytes ≈ 125K

```

And at peak, both exist at the same time:

```

125K + 125K = 250K

```

So the `250K` is simply:

Intermediate index matrix + final output matrix

So, the total allocated bytes over the time is roughly:

`25GB`

A litte bit memory hungry.

But we will be less in a minute.

## The Flat variant

We just changed the data to:

```C

const size_t a[] = {0,  1,  2,  3,  4};  
const size_t b[] = {10, 11, 12, 13, 14};                         
const size_t c[] = {20, 21, 22, 23, 24};                         
const size_t d[] = {30, 31, 32, 33, 34};                         
const size_t e[] = {40, 41, 42, 43, 44};                         

size_t data[25];

memcpy(data + 0,  a, sizeof(a));
memcpy(data + 5,  b, sizeof(b));
memcpy(data + 10, c, sizeof(c));
memcpy(data + 15, d, sizeof(d));
memcpy(data + 20, e, sizeof(e));

```

Hence, we just change the `makeMatrix` function to:

```C

void makeMatrix(Matrix2D *mat,
                const size_t *indices,
                const size_t *data,
                const size_t nrows,
                const size_t ndim,
                const size_t data_nrows
               ) {

    size_t *vec = mat->data;

    for (size_t i = 0; i < nrows; ++i) {
        const size_t base_pos = i * ndim;
        for (size_t i2 = 0; i2 < ndim; ++i2) {
            vec[base_pos + i2] = data[i2 * data_nrows + indices[base_pos + i2]];
        }
    }
}

```

### Benchmarks

Now, we just call it as:

```C

makeMatrix(&mat, 
           indices, 
           data,
           rows,
           ndim,
           lengths[0]);

```

Straight to results.

```

❯ ./cartesianb
iterations:       100000
elapsed:          1066087986 ns
ns / call:        10660.88
sink 4400000

```

Very nice, just gained arround `10%` in runtime speed.

Of course, because no memory difference, we got the same results from `heaptrack` than the last one.

```
PEAK MEMORY CONSUMERS
250.00K peak memory consumed over 300000 calls from
main
  in /home/juju/99HaskellProbs/cartesianb
125.00K consumed over 100000 calls from:
125.00K consumed over 100000 calls from:
```

That is always a good variant to test.

But still the fused variants to test.

## The C fused variants

Like the Haskell version, it's in fact just one function that will directly create the data, so no indices reuse possible, but who cares here, we just want to test one-shot perf!

We avoid huge `malloc` of indices here.

```C

void cartesian_product_matrix(
    Matrix2D *mat,
    const size_t *lengths,
    const size_t *data[],
    size_t ndim
) {
    size_t total = 0;

    if (!get_total_length(lengths, ndim, &total)) {
        return;
    }

    if (total == 0) {
        return;
    }

    if (ndim == 0) {
        return;
    }

    if (total > SIZE_MAX / ndim) {
        return;
    }

    size_t n_elems = total * ndim;

    if (n_elems > SIZE_MAX / sizeof(size_t)) {
        return;
    }

    mat->nrows = total;
    mat->ncols = ndim;
    mat->data = malloc(n_elems * sizeof(size_t));

    size_t *actual_data = mat->data;

    if (actual_data == NULL) {
        return;
    }

    size_t *cur_indices = calloc(ndim, sizeof(*cur_indices));
    if (cur_indices == NULL) {
        free(actual_data);
        mat->data = NULL;
        mat->nrows = 0;
        mat->ncols = 0;
        return;
    }

    size_t row = 0;
    size_t dim = ndim - 1;

    while (row < total) {
        const size_t row_idx = ndim * row;

        for (size_t i = 0; i < ndim; ++i) {
            actual_data[row_idx + i] = data[i][cur_indices[i]];
        }

        ++row;

        if (row == total) {
            break;
        }

        while (dim > 0 && cur_indices[dim] + 1 == lengths[dim]) {
            cur_indices[dim] = 0;
            --dim;
        }

        ++cur_indices[dim];
        dim = ndim - 1;
    }

    free(cur_indices);
}

```

### Benchmarks

The code is:

```C

int main(void) {

    const size_t a[] = {0,  1,  2,  3,  4};  
    const size_t b[] = {10, 11, 12, 13, 14};                         
    const size_t c[] = {20, 21, 22, 23, 24};                         
    const size_t d[] = {30, 31, 32, 33, 34};                         
    const size_t e[] = {40, 41, 42, 43, 44};                         

    const size_t *data[] = {a, b, c, d, e};

    const size_t lengths[] = {
        sizeof(a) / sizeof(a[0]),
        sizeof(b) / sizeof(b[0]),
        sizeof(c) / sizeof(c[0]),
        sizeof(d) / sizeof(d[0]),
        sizeof(e) / sizeof(e[0])
    };

    const size_t ndim = sizeof(lengths) / sizeof(lengths[0]);

    const size_t iterations = 100000;

    uint64_t start = now_ns();
    volatile size_t sink = 0;

    for (size_t i = 0; i < iterations; ++i) {
        Matrix2D mat;
        cartesian_product_matrix(&mat,
                                 lengths, 
                                 data,
                                 ndim);

        sink += mat.data[0];
        sink += mat.data[mat.nrows * ndim - 1];

        free(mat.data);
    }

    uint64_t end = now_ns();

    uint64_t elapsed_ns = end - start;

    double ns_per_iter = (double)elapsed_ns / (double)iterations;

    printf("iterations:       %zu\n", iterations);
    printf("elapsed:          %" PRIu64 " ns\n", elapsed_ns);
    printf("ns / call:        %.2f\n", ns_per_iter);

    printf("sink %zu\n", sink);

    return 0;
}

```

Straight to results again :)

```

❯ ./cartesian2
iterations:       100000
elapsed:          564512387 ns
ns / call:        5645.12
sink 4400000

```

Huuuge performance gain here, near half a second !

And what does `heaptrack` tell us ?

```

PEAK MEMORY CONSUMERS
125.04K peak memory consumed over 200000 calls from
main
  in /home/juju/99HaskellProbs/cartesian2
125.00K consumed over 100000 calls from:

```

Yes, less memory intensive as expected, over only `12GB` total allocated bytes over the time.

There are just allocations for the matrix vector and the tiny `cur_indices`.

Now it is time for the fused flat data variant !

## The fused flat data C variant

Here, just the access of the elements of `data` will change.

Remember, we got flat data:

```C

const size_t a[] = {0,  1,  2,  3,  4};  
const size_t b[] = {10, 11, 12, 13, 14};                         
const size_t c[] = {20, 21, 22, 23, 24};                         
const size_t d[] = {30, 31, 32, 33, 34};                         
const size_t e[] = {40, 41, 42, 43, 44};                         

size_t data[25];

memcpy(data + 0,  a, sizeof(a));
memcpy(data + 5,  b, sizeof(b));
memcpy(data + 10, c, sizeof(c));
memcpy(data + 15, d, sizeof(d));
memcpy(data + 20, e, sizeof(e));

```

So, in `cartesian_product_matrix`, we just change the `data` access part to:

```C

for (size_t i = 0; i < ndim; ++i) {
    actual_data[row_idx + i] = data[nval * i + cur_indices[i]];
}

```

The function signature changed to add `nval`.

```C

void cartesian_product_matrix(
    Matrix2D *mat,
    const size_t *lengths,
    const size_t *data,
    size_t ndim,
    size_t nval
) 

```

### Benchmarks

Now, we call it as:

```C

Matrix2D mat;
cartesian_product_matrix(&mat,
                         lengths, 
                         data,
                         ndim,
                         lengths[0]
);

```

RESULTS !

```

❯ ./cartesian2b
iterations:       100000
elapsed:          575563006 ns
ns / call:        5755.63
sink 4400000

```

Hmm, still good, but a little bit slower than the 2d flat data variant.

Why ?

I think because arithmetic cost of computing the index is NOT amortized by the pointer indirection the 2D data variant have.

And of course the `heaptrack` results stay the same from the previous version.

## Conclusion

First, a recap perf table:

| Version | Time | Allocated | Notes |
|---|---:|---:|---|
| Naive Haskell | 30.49s | 192.7GB | Index generation with lists |
| Haskell list comprehension | 4.81s | 31.4GB | Very close to native |
| Native Haskell `sequence` | 4.43s | 31.4GB | Baseline idiomatic version |
| Haskell vector general | 5.66s | 12.5GB | Less allocation, slower |
| Haskell vector flat special-case | 2.50s | 12.5GB | Beats native `sequence` |
| Haskell fused general | 6.09s | 12.5GB | Fusion not automatically better |
| Haskell fused flat special-case | 2.45s | 12.5GB | Fastest Haskell version |
| C unfused pointer data | 1.12s | 25GB | Manual memory + simple loops |
| C unfused flat special-case | 1.07s | 25GB | Slightly faster |
| C fused pointer data | 0.56s | 12GB | Fastest overall |
| C fused flat special-case | 0.58s | 12GB | Slightly slower than pointer data |







