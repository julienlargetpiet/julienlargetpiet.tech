Graph isomorphism is one of the classic challenges in graph theory and computer science.
It involves determining whether two graphs have the same structure — that is, whether one can be transformed into the other simply by relabeling its nodes.


I first encountered this problem through the
[99 Haskell Problems](https://wiki.haskell.org/index.php?title=99_questions/80_to_89),
specifically Problem 85.
It’s an elegant exercise that brings together recursion, list manipulation, and combinatorics.


## 1\. The problem

> Two graphs `G₁(N₁,E₁)` and `G₂(N₂,E₂)` are **isomorphic**
>  if there exists a bijection `f : N₁ → N₂` such that for any nodes `X, Y ∈ N₁`,
>  `X` and `Y` are adjacent if and only if `f(X)` and `f(Y)` are adjacent.

In other words, two graphs are isomorphic if they are structurally identical, regardless of how their nodes are labeled.


### Example

```haskell

λ> graphG1 = ([1,2,3,4,5,6,7,8],
               [(1,5),(1,6),(1,7),(2,5),(2,6),(2,8),
                (3,5),(3,7),(3,8),(4,6),(4,7),(4,8)])

λ> graphH1 = ([1,2,3,4,5,6,7,8],
               [(1,2),(1,4),(1,5),(6,2),(6,5),(6,7),
                (8,4),(8,5),(8,7),(3,2),(3,4),(3,7)])

λ> iso graphG1 graphH1
True
```

The two graphs are structurally identical, even though their connections differ by labeling.


## 2\. Representing graphs

As in earlier problems (such as Problem 81), the natural Haskell representation for a graph is:


```
([nodes], [(startingNode, endingNode)])
```

For instance:


```haskell

graphG1 = ([1,2,3,4,5,6,7,8],
            [(1,5),(1,6),(1,7),(2,5),(2,6),(2,8),
             (3,5),(3,7),(3,8),(4,6),(4,7),(4,8)]) :: ([Int], [(Int, Int)])

```

## 3\. The Haskell implementation

Below is my full implementation of the graph isomorphism check:


```haskell


iso :: (Eq a) => ([a], [(a, a)]) -> ([a], [(a, a)]) -> ([(a, a)], Bool)
iso (n1, ed1) (n2, ed2)
    | length n1 /= length n2   = ([], False)
    | length ed1 /= length ed2 = ([], False)
    | otherwise =
        let degreexs1 = quickSortAsc $ findDegree (n1, ed1)
            degreexs2 = quickSortAsc $ findDegree (n2, ed2)
        in if degreexs1 /= degreexs2
           then ([], False)
           else
               let outxs = findGraphPermutation (n1, ed1) (n2, ed2) degreexs1 degreexs2 ed1 ed2
               in (outxs, (length outxs) /= 0)


```

### Supporting functions

The rest of the code defines helper functions to compute degrees, group nodes, generate bijections, and test mappings:


```haskell


findGraphPermutation :: (Eq a) => ([a], [(a, a)]) ->
                        ([a], [(a, a)]) -> [Int] -> [Int] -> [(a, a)] -> [(a, a)] -> [(a, a)]
findGraphPermutation (n1, ed1) (n2, ed2) ids1 ids2 cmped1 cmped2 =
    let xs = groupByDegree ids1 n1 ids2 n2 (unique ids1)
    in subFindGraphPermutation xs cmped1 cmped2

groupByDegree :: (Eq a) => [Int] -> [a] -> [Int] -> [a] -> [Int] -> [([a], [a])]
groupByDegree _ _ _ _ [] = []
groupByDegree ids1 n1 ids2 n2 (cmp:nxs) =
    let g1 = map (\(_, curnode) -> curnode) (filter (\(val, _) -> val == cmp) (zip ids1 n1))
        g2 = map (\(_, curnode) -> curnode) (filter (\(val, _) -> val == cmp) (zip ids2 n2))
    in [(g1, g2)] ++ groupByDegree ids1 n1 ids2 n2 nxs

subFindGraphPermutation :: (Eq a) => [([a], [a])] -> [(a, a)] -> [(a, a)] -> [(a, a)]
subFindGraphPermutation [] _ _ = []
subFindGraphPermutation ((n1, n2):xs) cmped1 cmped2 =
    let permu = breakAt (map (\[x, y] -> (x, y)) (sequence [n1, n2]))
        permu2 = genBijections permu
        outxs = case (find (\vala -> testMapping vala cmped1 cmped2) permu2) of
                  Just x -> x
                  Nothing -> []
    in outxs ++ subFindGraphPermutation xs cmped1 cmped2

findDegree :: (Eq a) => ([a], [(a, a)]) -> [Int]
findDegree ([], _) = []
findDegree ((x:xs), nodexs) = [length $ filter (\(x1, y1) -> x1 == x || y1 == x) nodexs] ++ findDegree (xs, nodexs)

testMapping :: (Eq a) => [(a,a)] -> [(a,a)] -> [(a,a)] -> Bool
testMapping mapping ed1 ed2 =
  all (\e -> applyMapping mapping e `elem` ed2) ed1

applyMapping :: (Eq a) => [(a,a)] -> (a,a) -> (a,a)
applyMapping f (u,v) = (lookup2 u f, lookup2 v f)
  where
    lookup2 x mapping = case lookup x mapping of
                          Just y -> y
                          Nothing -> x

genBijections :: Eq b => [[(a,b)]] -> [[(a,b)]]
genBijections [] = [[]]
genBijections (grp:grps) =
    concat (map (\(src, tgt) -> let filteredgrps = map (filter (\(_, y) -> y /= tgt)) grps
                                in map ((src, tgt):) (genBijections filteredgrps))
                grp)
```

## 4\. How the algorithm works

The algorithm follows a logical sequence:


1. It first compares the number of nodes and edges in both graphs.
2. It computes the **degree sequence** of each graph — how many connections each node has.
3. If the degree sequences differ, the graphs can’t be isomorphic.
4. If they match, the algorithm attempts to find a valid bijection (a one-to-one mapping) between nodes that preserves adjacency.
5. Finally, it verifies whether applying that mapping to all edges in the first graph results in the exact set of edges in the second graph.

This last verification step is the core of the isomorphism test — it ensures that connections are preserved under the node mapping.


## 5\. Example result

```bash


ghci> iso graphG1 graphH1
(True, ...)
```

The result shows that the graphs are indeed isomorphic — they have identical structures.


## 6\. Why this is interesting

- Graph isomorphism sits in a fascinating complexity class:
   it’s not known to be either polynomial-time solvable or NP-complete (as of now).
- This Haskell approach doesn’t aim for computational efficiency but focuses on expressing
   the recursive and functional nature of the problem clearly.
- It demonstrates how combinatorial problems can be modeled cleanly with pure functions and immutable data.

## 7\. Wrap-up

Implementing graph isomorphism in Haskell beautifully showcases the language’s strengths:


- Declarative structure that mirrors mathematical definitions.
- List transformations to explore permutations and mappings.
- Recursion and higher-order functions to express algorithmic logic concisely.

While this version is not optimized for large graphs, it’s a clear and educational way
to understand how isomorphism can be expressed in functional programming.
Once again, Haskell turns a complex theoretical problem into elegant, composable code.


_Graph theory and Haskell — a perfect meeting point between mathematics and abstraction._