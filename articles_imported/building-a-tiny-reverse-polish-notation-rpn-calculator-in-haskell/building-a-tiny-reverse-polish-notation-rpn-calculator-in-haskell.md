In this project, we’ll build a small expression evaluator using **Reverse Polish Notation** (RPN) —
also called _postfix notation_. The idea is simple: instead of writing
`3 + 4`, you write `3 4 +`. This lets you evaluate expressions without worrying about
parentheses or operator precedence.


The project is a fun and compact way to learn about:


- Recursion
- Pattern matching
- List manipulation with `foldl`
- Function composition

## 1\. The goal

We want a function that can take a string like `"3 4 +"` and return `7.0`.
Or more complex ones like `"2 3 4 + *"` → `14.0`.


We’ll also add support for basic arithmetic, powers, exponentials, logs, and even a factorial!


## 2\. The full code

```haskell


primitiveSolver :: String -> Double
primitiveSolver expr = head . foldl funcNPI [] . words $ expr
    where funcNPI (x:ys) "!"      = (factorial2 x):ys
          funcNPI (x:ys) "exp"    = (exp x):ys
          funcNPI (x:ys) "log"    = (log x):ys
          funcNPI (x:y:ys) "**"   = (x ** y):ys
          funcNPI (x:y:ys) "*"    = (x * y):ys
          funcNPI (x:y:ys) "/"    = (x / y):ys
          funcNPI (x:y:ys) "+"    = (x + y):ys
          funcNPI (x:y:ys) "-"    = (x - y):ys
          funcNPI xs numberString = read numberString : xs

factorial2 :: (Floating a, Eq a) => a -> a
factorial2 0 = 1
factorial2 n = (*) n . factorial2 $ n - 1
```

## 3\. How it works

### `foldl` and the stack

The key idea is that RPN can be evaluated using a **stack**. You scan the expression token by token:


- If it’s a number, push it on the stack.
- If it’s an operator, pop the needed operands from the stack, compute, and push the result back.

The expression is split into tokens using `words`, and `foldl` traverses them left to right,
maintaining the stack as its accumulator.


At the end, `head` retrieves the top of the final stack — the result.


### The `funcNPI` function

This helper function defines what to do for each possible token:


- `(x:ys) "!"` → apply factorial to the top of the stack
- `(x:ys) "exp"` → apply exponential
- `(x:ys) "log"` → apply natural logarithm
- `(x:y:ys) "**"` → exponentiation
- Arithmetic operators ( `*`, `/`, `+`, `-`) pop two elements
- Otherwise, we assume the token is a number → convert with `read` and push onto the stack

The function relies heavily on **pattern matching** to destructure the stack
( `x:y:ys` means at least two elements available).


### The `factorial2` helper

This is a recursive factorial function defined for floating types:


```haskell

factorial2 0 = 1
factorial2 n = (*) n . factorial2 $ n - 1

```

It’s written in a point-free style using function composition
( `(*) n . factorial2 $ n - 1`) instead of the more traditional
`n * factorial2 (n - 1)` — a good reminder that Haskell lets you write recursion in many elegant ways.


## 4\. Examples

- `primitiveSolver "3 4 +"` → `7.0`
- `primitiveSolver "2 3 4 + *"` → `14.0`
- `primitiveSolver "5 !"` → `120.0`
- `primitiveSolver "2 3 **"` → `8.0`
- `primitiveSolver "1 exp"` → `2.718281828...`

## 5\. What you learn

- **Pattern matching** to destructure lists and handle multiple operator cases elegantly.
- **Recursion** for defining mathematical operations like factorial.
- **Folding** to replace explicit loops with declarative transformations.
- **Function composition** for building expressive, point-free recursive definitions.

## 6\. Wrap-up

This “primitive solver” might look small, but it’s a perfect example of Haskell’s power:
with just a few lines, you can build a stack-based interpreter capable of evaluating complex expressions.


And because it’s written in pure functional style, it reads more like a description of how to evaluate an expression
than a step-by-step algorithm. That’s the beauty of Haskell.