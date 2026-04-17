In this tutorial — inspired by my video _“Structure de données et système de types en Haskell”_ —
we dive into the heart of what makes Haskell so expressive: its **type system**.


This article targets an intermediate audience: you already know what a function or a list is,
but now you want to understand _why_ types in Haskell feel so different — and powerful — compared to other languages.


## 1\. Why types matter in Haskell

In Haskell, types are not just annotations — they are **first-class citizens** that
define how values behave and interact. The compiler (GHC) uses types to enforce correctness,
optimize performance, and even help you reason about your program.


Every value in Haskell has a type, and Haskell’s compiler infers those types automatically.
But you can (and should) write them explicitly to make your intent clear.


```haskell


add :: Int -> Int -> Int
add x y = x + y
```

This tells the compiler that `add` takes two integers and returns another integer.


## 2\. Type inference and polymorphism

Haskell’s compiler can infer types thanks to a mechanism called **Hindley–Milner type inference**.
For example, if you omit the type signature:


```haskell


  identity x = x


```

The compiler infers the most general type possible:


```haskell


  identity :: a -> a


```

Here, `a` is a **type variable**, meaning `identity` can work on any type —
integers, strings, lists, you name it. This is what we call **parametric polymorphism**.


## 3\. Typeclasses — defining shared behavior

A **typeclass** in Haskell defines a set of behaviors that different types can implement.
Think of it as an interface, but purely functional and extensible.


```haskell


  class Eq a where
  (==) :: a -> a -> Bool
  (/=) :: a -> a -> Bool


```

The `Eq` typeclass defines equality.
Any type that implements `Eq` must provide definitions for `(==)` and `(/=)`.


To make your own type an instance of `Eq`:


```haskell


data Color = Red | Green | Blue

instance Eq Color where
  Red   == Red   = True
  Green == Green = True
  Blue  == Blue  = True
  _     == _     = False


```

Now, you can compare `Color` values directly:


```haskell


Red == Blue   -- False
Green == Green -- True


```

## 4\. Custom data types and pattern matching

One of Haskell’s most elegant features is the ability to define your own data structures.
Let’s define a simple `Shape` type:


```haskell


  data Shape
  = Circle Float
  | Rectangle Float Float


```

You can now create shapes like `Circle 5` or `Rectangle 4 6`.
Pattern matching makes it trivial to extract values from these structures:


```haskell


area :: Shape -> Float
area (Circle r) = pi * r ^ 2
area (Rectangle w h) = w * h


```

Each constructor of the type is handled as a different pattern.
This is one of Haskell’s most powerful ways of structuring logic —
the compiler ensures you’ve covered all possible cases.


Very usefull when working on graphs and trees ;)

## 5\. Type synonyms and newtype

Sometimes you want to make your code more readable without introducing a new data constructor.
That’s where `type` and `newtype` come in.


```haskell


type Name = String
type Age = Int

data Person = Person Name Age


```

The `type` keyword doesn’t create a new type — it’s just an alias.
If you need a distinct type with a single underlying representation, use `newtype`:


```haskell


  newtype UserId = UserId Int


```

Unlike `type`, `newtype` creates a truly distinct type that can have its own
instances and behaviors, even though it’s represented by the same underlying value at runtime.


## 6\. Deriving standard behaviors

Instead of manually writing instances for basic behaviors like equality or printing,
Haskell lets you automatically derive them.


```haskell


  data Point = Point Float Float
  deriving (Show, Eq)


```

Now you can print and compare points directly:


```haskell


Point 2 3 == Point 2 3  -- True
print (Point 1 5)       -- "Point 1.0 5.0"


```

## 7\. Bringing it all together

The Haskell type system is not just about safety — it’s about expressing ideas clearly.
By using typeclasses, data definitions, and polymorphism,
you can make illegal states unrepresentable and describe the logic of your program at the type level.


- Types describe what’s possible.
- Typeclasses describe what’s _allowed_.
- Pattern matching reveals what’s _inside_.

Once you start thinking in types, your Haskell code becomes not only correct — but self-documenting.


## 8\. Wrap-up

In this intermediate overview, we explored:


- How type inference and polymorphism make functions generic
- What typeclasses are and how they model shared behavior
- How to define your own data types and pattern match on them
- When to use `type` vs `newtype`
- How deriving simplifies standard operations

In short, the Haskell type system isn’t just a safety net — it’s a design language.
Mastering it is the first real step toward writing expressive, composable, and reliable Haskell code.