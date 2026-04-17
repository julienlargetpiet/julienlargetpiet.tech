In this project, I set out to build my own version of the `sequence` function in Haskell —
a function that computes the **Cartesian product** of a list of lists.
While Haskell’s standard library already provides `sequence` for lists,
implementing it yourself is a fantastic way to learn about recursion, indexing,
and how list comprehensions work under the hood.


This project was inspired by the video _“Produit cartésien des éléments dans une liste aux autres”_,
where I explored how to generate all combinations of elements across several lists manually.


## 1\. The idea behind the algorithm

The goal is to generate every possible combination of elements such that:


```
[[x1, x2, ...], [y1, y2, ...], [z1, z2, ...]]
```

becomes something like:


```
[[x1, y1, z1], [x1, y1, z2], [x1, y2, z1], [x2, y1, z1], ...]
```

This is a full Cartesian product across multiple dimensions.


## 2\. The full Haskell implementation

```haskell


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

## 3\. Step-by-step breakdown

The process can be understood as a multi-dimensional counter:


- `mySequencePrepareLength` computes the length of each sublist,
   so the algorithm knows how many elements each dimension can hold.
- `mySequencePrepareIds` initializes an index list like `[0, 0, 0, ...]`
   to keep track of which element to pick in each sublist.
- `mySequenceIdsn` generates all possible index combinations recursively.
- `mySequenceList` uses those indices to build actual list combinations.

## 4\. The recursive iteration logic

The most interesting part is `mySequenceIdsn`,
which behaves like a nested loop generator — but without using explicit loops.


- If the last index hasn’t reached its limit yet, increment it (like increasing the least significant digit in a counter).
- If it reaches its maximum, reset it to 0 and move one level up — like when 999 rolls over to 1000.
- This recursive carry-over process continues until all combinations have been generated.

The three small helpers `subMySequence`, `subMySequence2`,
and `subMySequence3` handle different aspects of this index adjustment process.


## 5\. Testing the function

Let’s test the function with a small example:


```haskell

main = print (mySequence [[1,2], [3,4], [5,6]])

```

The expected output is:


```
[[1,3,5],[1,3,6],[1,4,5],[1,4,6],[2,3,5],[2,3,6],[2,4,5],[2,4,6]]
```

Which corresponds exactly to the full Cartesian product of the three input lists.


## 6\. Why build it yourself?

While Haskell’s built-in `sequence` or `mapM` functions already handle this,
implementing it yourself offers valuable insight:


- You learn how recursion replaces loops elegantly.
- You see how indices can model a combinatorial space.
- You discover how pure functional programming can express nested iteration.

It’s also a great exercise in **recursion with state carried through immutable data**:
the “state” of our index list evolves through recursive calls, without mutating anything.


## 7\. Wrap-up

This project demonstrates how recursive functions can emulate the behavior of imperative loops
— systematically generating all combinations across multiple lists.


Through `mySequence`, we built a small but powerful algorithmic pattern:


- Base case: empty input returns nothing.
- Recursive case: update indices, generate new combinations, continue until limits are reached.

The result is a pure, mathematical way of building the Cartesian product,
which deepens your understanding of Haskell’s approach to recursion and list construction.


_In essence, we reinvented the “nested for loops” — the Haskell way._