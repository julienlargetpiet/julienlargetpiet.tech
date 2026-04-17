Recursion often feels like a mysterious concept when you first encounter it — until you realize that it’s not about doing something repeatedly, but about **breaking a problem into smaller, self-similar parts**.
In this post, we’ll explore how recursion allows us to generate combinations, random permutations, and even manipulate trees and graphs elegantly in Haskell.


To begin, here’s how I once described it:


> “So when my program makes its first recursive call, what does it actually do?
> Does it launch another recursive call with a different input?”
>
>
> The answer is yes — it destructures the input string, taking its first element, say “a”.
>
>
> If we follow only that first recursive call, it will generate “abc”.
> But notice that when it took “a”, it also made another recursive call — this time with a different input, “bcdef”.
>
>
> That second call will generate “bcd”, and so on.
> We can extrapolate this to all inputs: when we have “ab”, we also launch on “cde”, etc.

That’s the essence of recursion: each call is not isolated — it _branches_ into new calls, each exploring a smaller or alternative subset of the problem.


## 1\. Generating combinations recursively

Let’s start with a classic recursive problem: generating all combinations of a list.
Given a list and a number `k`, we want all subsets of size `k`.


```haskell

combinations :: Int -> [a] -> [[a]]
combinations 0 _ = [[]]
combinations _ [] = []
combinations k (x:xs) =
    map (x:) (combinations (k - 1) xs) ++ combinations k xs


```

The idea is simple but beautifully recursive:


- If we choose the current element `x`, we combine it with combinations of size `k - 1` from the rest of the list.
- If we skip `x`, we just generate combinations of size `k` from the remaining list.

Each recursive step _splits_ the search space, creating two new recursive paths.
This branching continues until we reach the base case — when `k == 0` or the list is empty.


For example:


```
combinations 2 "abc"
```

The recursion tree will explore paths like:


- Take 'a' → then choose from "bc"
- Skip 'a' → choose from "bc"

The final result: `["ab", "ac", "bc"]`.


## 2\. Random permutations through recursion

Recursion is also at the core of generating random permutations.
Here’s one of my implementations that constructs a random permutation of a list:


```haskell


rnd_permu :: (Eq a) => [a] -> [a]
rnd_permu xs = subRnd_Permu l xs (R.mkStdGen l) 0 []
    where l = length xs

subRnd_Permu :: (Eq a) => Int -> [a] -> R.StdGen -> Int -> [a] -> [a]
subRnd_Permu l xs gen n2 xs2
    | n2 < l =
        let (val, newgen) = R.random gen
            idx = val `mod` l
            myval = xs !! idx
        in if myval `elem` xs2
           then subRnd_Permu l xs newgen n2 xs2
           else subRnd_Permu l xs newgen (n2 + 1) (myval:xs2)
    | otherwise = xs2
```

Here recursion manages both the _state evolution_ (through the random generator)
and the _constraint checking_ (avoiding duplicates).
Each recursive call either appends a new unique element or retries with a fresh random seed.


When all elements are used, the recursion unwinds, leaving a complete random permutation.


## 3\. Trees and structural recursion

When we move from lists to structures like trees or graphs, recursion becomes even more natural.
A tree is inherently recursive — it’s defined as a node that may contain two smaller trees.


```haskell


  data MyTree a = MyEmpty | MyNode a (MyTree a) (MyTree a)
  deriving (Show, Eq)


```

Now let’s look at a very elegant function (not mine, but one I really appreciate) —
generating **completely balanced binary trees**.


```haskell


cbalTree :: Int -> [(MyTree Char)]
cbalTree 0 = [MyEmpty]
cbalTree 1 = [MyNode 'x' MyEmpty MyEmpty]
cbalTree n =
    if n `mod` 2 == 1 then
      [ MyNode 'x' l r
      | l <- cbalTree ((n - 1) `div` 2)
      , r <- cbalTree ((n - 1) `div` 2) ]
    else
      concat
        [ [MyNode 'x' l r, MyNode 'x' r l]
        | l <- cbalTree ((n - 1) `div` 2)
        , r <- cbalTree (n `div` 2) ]
```

This function recursively builds all balanced binary trees of a given size.
The recursion mirrors the structure of the tree itself: each recursive call constructs smaller subtrees
and combines them symmetrically.


To check symmetry, we can write:


```haskell


isSymetric :: (Eq a) => (MyTree a) -> Bool
isSymetric (MyNode _ l r) = l == r
```

The beauty here is in its simplicity — we let Haskell’s equality operator recursively compare each branch automatically.


## 4\. The unifying theme: recursion as exploration

Whether you’re dealing with combinations, permutations, or trees, recursion gives you a natural way
to **explore all possibilities** without ever writing a loop.


- In combinations, recursion explores subsets.
- In permutations, recursion explores all orderings.
- In trees, recursion explores branches and structure.

The only difference is what each recursive call represents —
a smaller list, a reduced pool of choices, or a smaller subtree.


Conceptually, every recursive call is like a traveler walking one step further down a decision path,
and every base case is that traveler saying, “I’ve reached the end — time to return.”


## 5\. Wrap-up

Recursion in Haskell isn’t a trick — it’s the language’s way of _thinking_.
It provides a mental model for describing exploration, branching, and structure in a clear and functional way.


- Combinations show how recursion enumerates possibilities.
- Permutations show how recursion enforces constraints.
- Trees show how recursion naturally mirrors data structure.

Once you start visualizing recursion as a network of simultaneous explorers,
each moving down its own branch of a decision tree, recursion stops feeling abstract —
it becomes the most natural way to think about combinatorial and structural problems.