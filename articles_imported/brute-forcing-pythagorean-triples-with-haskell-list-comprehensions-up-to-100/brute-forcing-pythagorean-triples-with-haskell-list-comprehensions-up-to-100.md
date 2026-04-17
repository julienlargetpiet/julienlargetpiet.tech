## Introduction

We want all integer solutions `(a,b,c)` to the equation
`a^2 = b^2 + c^2` with `0 < a < 100`. This is a great place to use Haskell’s
list comprehensions: they’re concise, readable, and—when bounded carefully—surprisingly efficient.


## The goal (and a small symmetry trick)

We’re after triples `(a,b,c)` that satisfy:


- `a^2 = b^2 + c^2`
- `0 < a < 100`
- to avoid duplicates from swapping legs, we enforce **ordering**: `c < b < a`

That last line is key: every valid solution has one leg greater or equal to the other, so we arbitrarily
choose `b` to be the larger leg and enforce `c < b`. This removes mirrored duplicates.


## Important list comprehension fact

In a Haskell list comprehension, a variable can be used only if it’s defined earlier in the same comprehension.
In other words, each generator or guard can reference only variables bound by _previous_ generators/guards.
So if `c` depends on the current `b`, you must generate `b` before `c`.


## Bounding the search (“bottlenecking”)

Two simple, powerful constraints:


1. Since `a` is generated in `[1..100]` and `a^2 = b^2 + c^2`, both legs must be
    strictly smaller than `a`. So we bottleneck `b` and `c` to be less than the current `a`.

2. To remove duplicates, we further bottleneck by ordering the legs: we choose `c` to range only up to `b-1`,
    i.e. `c < b`.


This shrinks the search space dramatically compared to a naive `[1..100]^3` sweep and makes the code clearer.


## The Haskell one-liner

```haskell

triples :: [(Int, Int, Int)]
triples =
  [ (a,b,c)
  | a <- [1..100]     -- 0<a<=100
  , b <- [1..a-1]     -- b<a  (so b<=99 automatically)
  , c <- [1..b-1]     -- c<b  (our symmetry break)
  , a*a == b*b + c*c  -- Pythagorean condition
  ]

```

**Why this order?**

- `a` is outermost (it sets the current “ceiling”).
- `b` depends on `a` (must be smaller), so it comes next.
- `c` depends on `b` (must be smaller), so it comes after `b`.
- Finally, the guard filters to valid triples.

Remember: you cannot write `c <- [1..b-1]` before `b` exists—the comprehension order matters.


## Examples you’ll get (with `c < b < a`)

- Smallest: `(5,4,3)`
- Classics: `(13,12,5)`, `(25,20,15)`, `(29,21,20)`
- Near the top end: `(91,84,35)`, `(95,76,57)`, `(97,72,65)`, `(100,80,60)`, `(100,96,28)`

## Optional refinements

- **Euclid’s formula (primitive triples):**
   generate coprime `m>n` with opposite parity and set
   `a = k(m^2+n^2)`, `b = k(2mn)`, `c = k(m^2-n^2)`, scaling `k` while
   `a < 100`.

- **Early pruning:** in strict loop styles, once `b*b + c*c > a*a` for growing `c`,
   you can break. With these bounded comprehensions, the overhead is already small.


## Takeaways

- **Scope rule:** in a comprehension, each variable is only in scope after it’s introduced.
- **Bottleneck early:** since `a < 100`, restrict `b,c < a` to cut the search space.
- **Exploit symmetry:** enforce `c < b` to avoid duplicate leg permutations.
- With these in place, you get a tiny, expressive enumerator for all solutions with `c < b < a < 100`.