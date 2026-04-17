The **Eight Queens Problem** is one of the most famous challenges in computer science and mathematics.
The goal is simple to state yet surprisingly rich in structure:
_Place eight queens on a chessboard so that no two queens threaten each other._

In practice, that means ensuring that no two queens share the same row, column, or diagonal.
It’s a classical example of a **constraint satisfaction problem** —
and an elegant one to tackle using Haskell’s declarative and recursive strengths.


## 1\. The problem restated

We must place 8 queens on an 8×8 chessboard so that:


- No two queens share the same column.
- No two queens share the same row.
- No two queens share the same diagonal (both ascending and descending).

We’ll represent each solution as a list of 8 integers,
where the index of the list corresponds to the column, and the value at that index is the row of the queen.


For example: `[4,2,7,3,6,8,5,1]` means:


- In column 1, place a queen in row 4.
- In column 2, place a queen in row 2.
- In column 3, place a queen in row 7.
- …and so on.

This representation makes the problem much easier to model with Haskell lists and recursion.


## 2\. My Haskell solution

I implemented a solution using the **generate-and-test** approach:
generate all possible queen placements, and recursively test which ones are valid.


```haskell


queens :: [[Int]]
queens =
    let outxs = map (\[c, r] -> (c, r)) (sequence [[1..8], [1..8]])
    in subQueens (zip outxs (replicate 64 False)) []

subQueens :: [((Int, Int), Bool)] -> [Int] -> [[Int]]
subQueens xs outval =
    let col = length outval + 1
        outxs = filter (\((c, r), alrd) -> c == col && not alrd && not (r `elem` outval)) xs
    in if col > 8
       then [outval]
       else concat [ subQueens (updateChess c r xs) (outval ++ [r])
                   | ((c,r),_) <- outxs ]

updateChess :: Int -> Int -> [((Int, Int), Bool)]
                -> [((Int, Int), Bool)]
updateChess c r xs =
    let newxs1 = map (\((v1, v2), alrd) -> if v1 == c || v2 == r
                                       then ((v1, v2), True)
                                       else ((v1, v2), alrd)) xs
        newxs2 = upperLeft newxs1 (c - 1) (r - 1)
        newxs3 = upperRight newxs2 (c + 1) (r - 1)
        newxs4 = lowerLeft newxs3 (c - 1) (r + 1)
        newxs5 = lowerRight newxs4 (c + 1) (r + 1)
    in newxs5

-- mark diagonals recursively
upperLeft, upperRight, lowerLeft, lowerRight :: [((Int, Int), Bool)] -> Int -> Int -> [((Int, Int), Bool)]

upperLeft xs 0 _ = xs
upperLeft xs _ 0 = xs
upperLeft xs c r =
    let newxs = map (\((x, y), alrd) -> if x == c && y == r
                                           then ((x, y), True)
                                           else ((x, y), alrd)) xs
    in upperLeft newxs (c - 1) (r - 1)

upperRight xs 9 _ = xs
upperRight xs _ 0 = xs
upperRight xs c r =
    let newxs = map (\((x, y), alrd) -> if x == c && y == r
                                           then ((x, y), True)
                                           else ((x, y), alrd)) xs
    in upperRight newxs (c + 1) (r - 1)

lowerLeft xs 0 _ = xs
lowerLeft xs _ 9 = xs
lowerLeft xs c r =
    let newxs = map (\((x, y), alrd) -> if x == c && y == r
                                           then ((x, y), True)
                                           else ((x, y), alrd)) xs
    in lowerLeft newxs (c - 1) (r + 1)

lowerRight xs 9 _ = xs
lowerRight xs _ 9 = xs
lowerRight xs c r =
    let newxs = map (\((x, y), alrd) -> if x == c && y == r
                                           then ((x, y), True)
                                           else ((x, y), alrd)) xs
    in lowerRight newxs (c + 1) (r + 1)


```

## 3\. How it works

### Step 1 — Representing the chessboard

The board is represented as a list of all 64 possible positions,
each paired with a Boolean flag indicating whether it’s available:


```
[((col, row), isTaken)]
```

Initially, all squares are free (all flags are `False`).


### Step 2 — Recursively placing queens

The function `subQueens` tries to place a queen column by column:


- At each step, it filters the available squares in the current column.
- It ensures no two queens share the same row ( ``not (r `elem` outval)``).
- It then recursively proceeds to the next column, marking all attacked squares as taken.

### Step 3 — Marking attacked squares

Once a queen is placed, the `updateChess` function marks:


- All squares in the same row and column.
- All squares on the four diagonals (using recursive directional functions).

The recursion stops once all 8 queens are placed, producing a valid configuration.


## 4\. Testing the solution

Running the function:


```haskell

λ> length queens
92

λ> head queens
[1,5,8,6,3,7,2,4]

```

Haskell finds all **92 valid solutions** to the classic 8-Queens problem.
Each list represents a unique arrangement of queens that do not attack each other.


## 5\. Why this approach is interesting

This implementation is a pure and explicit exploration of how backtracking works.
Unlike higher-level libraries that hide the recursion, here we clearly see:


- The search space being reduced as the board updates.
- The recursive nature of the generate-and-test process.
- How immutable data (the board state) is rebuilt at each step rather than mutated.

The `updateChess` logic mimics how a human would reason about threats on a board —
marking attacked zones before moving on.


## 6\. Reflection

Writing this in Haskell emphasizes how recursion, immutability, and list comprehensions combine
to form a natural framework for solving constraint-based problems.


The eight queens problem is not just a puzzle — it’s a microcosm of **search problems**
in computer science, from optimization to AI planning.


_With a few elegant recursive functions, Haskell transforms a complex constraint system_
_into a readable and mathematical solution._