The **Goldbach Conjecture** is one of the oldest unsolved problems in mathematics.
It states that _every even integer greater than 2 can be expressed as the sum of two prime numbers_.


While no formal proof has been found, the conjecture has been verified by computers for very large numbers.
In this post, we’ll explore how to express this idea recursively in Haskell — using an elegant search through the space of prime pairs.


## 1\. Restating the problem

For any even number `x > 2`, find two primes `p1` and `p2` such that:


```
p1 + p2 = x
```

For example:


- `4 = 2 + 2`
- `6 = 3 + 3`
- `10 = 5 + 5` or `7 + 3`

The challenge is to find such a pair efficiently — and recursion provides a natural way to iterate through potential candidates.


## 2\. The full implementation

Let’s look at my implementation of the Goldbach function in Haskell:


```haskell


goldbach :: Int -> (Int, Int)
goldbach x = subGoldbach x 1 (subGoldbachDesc x)

subGoldbach :: Int -> Int -> Int -> (Int, Int)
subGoldbach x v1 v2 =
    let (newv1, newv2) = updateInterval v1 v2
    in if (v1 + v2) == x
       then (v1, v2)
       else subGoldbach x newv1 newv2

updateInterval :: Int -> Int -> (Int, Int)
updateInterval v1 v2
    | v1 == v2 = (1, subGoldbachDesc v2)
    | otherwise = (subGoldbachAsc (v1 + 1) v2, v2)

subGoldbachDesc :: Int -> Int
subGoldbachDesc 1 = 1
subGoldbachDesc x
    | isPrime x = x
    | otherwise = subGoldbachDesc (x - 1)

subGoldbachAsc :: Int -> Int -> Int
subGoldbachAsc x cmp
    | x == cmp = cmp
    | isPrime x = x
    | otherwise = subGoldbachAsc (x + 1) cmp
```

Note that the function `isPrime` is assumed to exist — it checks if a number is prime.
The rest of the program is a clean, recursive search over possible prime pairs.


## 3\. How it works

The entry point `goldbach` begins with two values:


- `v1 = 1` — the lower bound that will grow upward.
- `v2 = subGoldbachDesc x` — the largest prime less than or equal to `x`.

Then, `subGoldbach` checks whether the current pair `(v1, v2)` satisfies the Goldbach condition:


- If `v1 + v2 == x` → success! We found a valid pair.
- Otherwise, we recursively update `v1` and `v2` and try again.

The function `updateInterval` moves our search boundaries:


- If both sides meet ( `v1 == v2`), we reset `v1` and find a smaller upper prime.
- Otherwise, we find the next prime ascending from `v1 + 1` using `subGoldbachAsc`.

## 4\. Descending and ascending through primes

Two helper functions are at the heart of the search: `subGoldbachDesc` and `subGoldbachAsc`.


`subGoldbachDesc` finds the largest prime less than or equal to `x`:


```haskell


subGoldbachDesc :: Int -> Int
subGoldbachDesc 1 = 1
subGoldbachDesc x
    | isPrime x = x
    | otherwise = subGoldbachDesc (x - 1)
```

Meanwhile, `subGoldbachAsc` finds the next prime greater than or equal to a given number, but not exceeding a comparison limit:


```haskell


subGoldbachAsc :: Int -> Int -> Int
subGoldbachAsc x cmp
    | x == cmp = cmp
    | isPrime x = x
    | otherwise = subGoldbachAsc (x + 1) cmp
```

These two recursive helpers define the upward and downward motion through the prime number space,
continuously adjusting our pair candidates until a valid combination is found.


## 5\. Step-by-step intuition

Think of the algorithm as two pointers moving inside a shrinking window:


- **The descending pointer** starts from the top (largest prime ≤ x).
- **The ascending pointer** starts from the bottom (smallest prime ≥ 2).

At each recursive step:


1. Check if `v1 + v2 == x`.
2. If not, move `v1` upward to the next prime.
3. If `v1` catches up to `v2`, move `v2` downward to the next smaller prime and restart `v1`.

Eventually, recursion guarantees that all possible pairs of primes are checked,
and the first valid one is returned as the Goldbach decomposition.


## 6\. Example

Let’s run an example:


```haskell


  main = print (goldbach 28)


```

Suppose `subGoldbachDesc 28` gives us `v2 = 23`.
Then recursion begins:


- Try (v1, v2) = (1, 23) → 24 ≠ 28
- Next primes: (5, 23) → 28 ✅ success!

The function returns `(5, 23)`, one valid Goldbach pair for 28.


## 7\. Why recursion fits perfectly here

The structure of the Goldbach problem is _naturally recursive_:
each step depends only on a smaller subproblem — finding the next suitable primes.


- `subGoldbachDesc` and `subGoldbachAsc` handle prime traversal recursively.
- `subGoldbach` recursively tests combinations of primes.
- The recursion terminates as soon as the condition `v1 + v2 == x` is met.

It’s a perfect example of functional recursion as an elegant search mechanism — no mutable state,
no explicit loops, just pure logical flow.


## 8\. Wrap-up

The Goldbach Conjecture may remain unproven, but in Haskell, we can express its logic clearly and functionally.


- Recursion acts as the engine of exploration.
- Each helper isolates a single behavior (ascend, descend, update, test).
- The result is a compact and readable algorithm mirroring mathematical reasoning.

Whether or not Goldbach is ever proven true, one thing is certain:
recursion in Haskell provides one of the cleanest ways to **think like a mathematician** in code.