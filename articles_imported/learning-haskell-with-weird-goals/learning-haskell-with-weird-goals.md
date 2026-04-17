Sometimes, the best way to learn a language is by using a simple, even slightly “weird” goal as an excuse to explore
its core concepts. Here, the goal is to extract the sides (apart from the hypotenuse) from a list of
Pythagorean triples—but really, it’s just a reason to learn how pattern matching, recursion, and
`let` blocks work in Haskell.


## 1\. A simple pattern-matching refresher

In Haskell, you can deconstruct tuples directly in function arguments. It’s an elegant and expressive way to
“take apart” data structures. Let’s define three simple functions to get each element from a 3-tuple:


```haskell

myFst :: (Int, Int, Int) -> Int
myFst (x, _, _) = x

mySnd :: (Int, Int, Int) -> Int
mySnd (_, x, _) = x

myThrd :: (Int, Int, Int) -> Int
myThrd (_, _, x) = x
```

The underscores ( `_`) mean “I don’t care about this value.” Only the variable names you use (like
`x`) are bound.


## 2\. Writing a recursive extractor

Let’s say we have a list of triples representing `(a, b, c)` values (like Pythagorean triples). We want to extract
two lists: one with the first element of each triple, and one with the second.


We can do this recursively:

```haskell

myExtractor :: [(Int, Int, Int)] -> ([Int], [Int])
myExtractor [] = ([], [])
myExtractor (x:xs) = ((myFst x):xs1, (mySnd x):xs2)
    where (xs1, xs2) = myExtractor xs

```

Let’s break this down:


- `(x:xs)` matches a non-empty list: `x` is the head, and `xs` is the tail.
- The base case `[]` returns two empty lists.
- The recursive call `myExtractor xs` gives you two partial results, bound in the
   `where` clause as `(xs1, xs2)`.
- Finally, we prepend the first and second elements of `x` to each list using `:`.

This pattern—matching the head/tail, then combining recursive results—is the backbone of functional recursion in Haskell.


## 3\. Introducing `let` blocks

The `where` clause is great for binding helper values, but sometimes you need more control over the scope.
That’s where `let` and `in` come in. Here’s a version of `myExtractor` that uses them:


```haskell

myExtractor2 :: [(Int, Int, Int)] -> ([Int], [Int])
myExtractor2 [] = ([], [])
myExtractor2 (x:xs) =
    let (xs1, xs2) = myExtractor xs
        a = 3
    in (((myFst x) + a):xs1, (mySnd x):xs2)

```

This version does the same thing, but introduces a new local variable `a` (which we arbitrarily add to
`myFst x`) to illustrate that you can define intermediate values with `let`. The syntax is:


```haskell

let bindings in expression

```

Everything defined in the `let` section is available inside the `in` expression, but not outside.


## 4\. Why this matters

- **Pattern matching** replaces manual “tuple unpacking.”
- **Recursion** replaces loops and accumulators, keeping functions declarative.
- **`let` blocks** give you local binding power—great for clarity and immutability.

## 5\. A playful mental model

Think of pattern matching as “cutting open” your data, recursion as “peeling through the list one layer at a time,”
and `let` as “taking notes along the way.” Each tool builds a different piece of Haskell’s elegant simplicity.


## 6\. Wrap-up

Our little “extract the sides” exercise might seem arbitrary, but it’s a perfect excuse to explore three of Haskell’s
most important ideas. Once you’re comfortable with these, you’ll find yourself using them everywhere—pattern matching
for data access, recursion for iteration, and `let` or `where` for organizing logic cleanly.