One of the most fascinating and ancient problems in recreational mathematics is the **Knight’s Tour** — the challenge of moving a chess knight so that it visits every square of an N×N chessboard exactly once.

It’s not just a puzzle: it’s a deep exploration of **backtracking**, **graph traversal**, and even **heuristic search**.

In this post, I’ll show how I implemented the Knight’s Tour in Haskell — first using a basic DFS (Depth-First Search), and then improved it with **Warnsdorff’s rule**, a clever heuristic that dramatically improves performance.

## ♟️ The Problem

The knight’s movement pattern is unique: it moves two squares in one direction and one in the perpendicular direction.

In coordinates, from position `(x, y)`, it can move to:

```
(x ± 2, y ± 1) or (x ± 1, y ± 2)
```

The challenge:

> Find a sequence of 64 moves (for an 8×8 board) such that each square is visited exactly once.

- **Open tour:** start and end anywhere.
- **Closed tour:** the last square connects back to the first via a legal knight move.

## 🧠 Step 1 – The Depth-First Search (DFS) Approach

My first implementation was a pure **DFS backtracking search**. It tries every possible knight move recursively, backtracking when a move leads to a dead end.

```haskell


knightsTo :: (Int, Int) -> [(Int, Int)]
knightsTo (c, r) =
    let chessboard = zip ([(x,y) | x <- [1..8], y <- [1..8]]) (replicate 64 False)
        newchessboard = map (\((x1, x2), alrd) -> if x1 == c && x2 == r
                                                  then ((x1, x2), True)
                                                  else ((x1, x2), alrd)) chessboard
    in map fst (subKnightsTo newchessboard [((c, r), 1)])
```

This function tries all 8 possible moves, updating the chessboard each time. When no valid move remains, it backtracks — marking the last square as unvisited.

It works… but very slowly. There are **billions** of possible paths on an 8×8 board, so pure DFS can take forever.

## ⚙️ Step 2 – Enter Warnsdorff’s Rule

**Warnsdorff’s heuristic** is a brilliant observation from 1823:

> “Always move the knight to the square with the fewest onward moves.”

The intuition is simple:

- If you go to a square with many options, you might paint yourself into a corner later.
- If you always pick the most constrained square, you tend to leave yourself room to move.

This heuristic doesn’t guarantee a solution — but it dramatically increases the chances and speed.

I combined this heuristic with DFS to create an elegant, efficient hybrid.

## 🚀 Step 3 – DFS + Warnsdorff Implementation

```haskell


import qualified Data.Array as A
import Data.List (sortOn)

type Pos = (Int, Int)
type Board = A.Array Pos Bool

-- Initialize 8x8 board
initBoard :: Board
initBoard = A.array ((1,1), (8,8)) [((x,y), False) | x <- [1..8], y <- [1..8]]

-- Knight moves
knightMoves :: Pos -> [Pos]
knightMoves (c,r) = filter onBoard
    [ (c+2,r+1), (c+2,r-1), (c-2,r+1), (c-2,r-1)
    , (c+1,r+2), (c+1,r-2), (c-1,r+2), (c-1,r-2)
    ]
  where onBoard (x,y) = x >= 1 && x <= 8 && y >= 1 && y <= 8

-- Warnsdorff sorting: prioritize constrained moves
sortByDegree :: Board -> [Pos] -> [Pos]
sortByDegree board = sortOn (\p -> length . filter (not . (board A.!)) $ knightMoves p)

-- Depth-first search
knightDFS :: Board -> Pos -> [Pos] -> Maybe [Pos]
knightDFS board pos path
    | length path == 64 = Just (reverse path)
    | otherwise =
        let board' = board A.// [(pos, True)]
            moves  = sortByDegree board' $ filter (not . (board' A.!)) (knightMoves pos)
        in tryMoves board' moves path
  where
    tryMoves _ [] _ = Nothing
    tryMoves b (m:ms) p =
        case knightDFS b m (m:p) of
            Just tour -> Just tour
            Nothing   -> tryMoves b ms p

-- Entry point
betterKnightTo2 :: Pos -> Maybe [Pos]
betterKnightTo2 start = knightDFS initBoard start [start]
```

## 🧩 How It Works

1. `initBoard` creates an 8×8 grid of `False` values (unvisited squares).
2. `knightMoves` lists all possible knight jumps that stay within bounds.
3. `sortByDegree` applies Warnsdorff’s rule — sorting next moves by the number of onward moves.
4. `knightDFS` recursively explores moves, marking positions as visited.
5. **Backtracking:** if a path dead-ends, the recursion unwinds and tries the next move.

Because of the heuristic ordering, the DFS rarely has to backtrack much — in most cases, it finds a complete tour almost immediately.

## 💡 Example Run

```haskell


  λ> betterKnightTo2 (1,1)
Just [(1,1),(3,2),(5,1),(7,2),(8,4), ... (2,3)]

```

It outputs one valid knight’s tour starting from (1,1). You can visualize it as a continuous path covering every cell exactly once.

## 🧮 Complexity and Performance

- **Naive DFS:** exponential in N². Practically infeasible for 8×8.
- **DFS + Warnsdorff:** near-linear average runtime — solves in under a second.
- **Pure Warnsdorff (no backtracking):** even faster but may fail for certain starts.

This hybrid balances completeness (DFS ensures a solution) with efficiency (Warnsdorff guides the search).

## 🔍 Closing Thoughts

The Knight’s Tour problem is a beautiful blend of **graph traversal**, **backtracking**, and **heuristic reasoning**. Implementing it in Haskell highlights how cleanly recursion can express complex search logic.

> "The knight moves through the board not by brute force, but by intuition — and a touch of functional elegance."

### Key Takeaways

- Representing the board functionally with immutability keeps logic pure.
- Warnsdorff’s heuristic transforms a brute-force search into a guided one.
- DFS remains the foundation — heuristics just make it smarter.