In graph theory, a **spanning tree** of a connected graph is a subgraph that includes all the nodes
of the original graph, connected with the minimum number of edges (exactly `n − 1` for `n` nodes)
and without any cycles.


I discovered this concept through
[Problem 83](https://wiki.haskell.org/index.php?title=99_questions/80_to_89)
of the _99 Haskell Problems_ series.
The goal is to construct, by backtracking, all spanning trees of a given graph,
and then use that logic to check if a graph is a tree or if it’s connected.


## 1\. The problem

> Write a function `spanningTree` that constructs (by backtracking) all spanning trees of a given graph.

Once we have that, we can easily define two related functions:


- `is_tree(Graph)` — determines if a graph is a tree.
- `is_connected(Graph)` — determines if a graph is connected.

For example, with the graph `k4` (the complete graph on 4 nodes):


```
λ> length $ spanningTree k4
16
```

There are 16 distinct spanning trees for `k4`.


## 2\. Representing graphs in Haskell

As usual, we represent a graph as a pair:


```
([nodes], [(startNode, endNode)])
```

For instance:


```
myGraph = (['a','b','c','d'],
           [('a','b'), ('a','c'), ('b','c'), ('b','d'), ('c','d')])
```

This means the graph has four nodes and five edges.


## 3\. The full implementation

```haskell


spantree2 :: ([Char], [(Char, Char)]) -> [([Char], [(Char, Char)])]
spantree2 (xs, ys) = filter isConnected $ filter noncycle alltrees
   where
      alltrees = [((uniqueval edges), edges) | edges <- foldr acc [[]] ys]
      acc e es = es ++ (map (e:) es)
      uniqueval e = foldr (\x xs -> if x `elem` xs then xs else x:xs)
             [] (concat $ map (\(a, b) -> [a, b]) e)
      noncycle (xs', ys') = length xs - 1 == length ys'
```

## 4\. Checking connectivity

The `isConnected` function ensures that all nodes in the graph are reachable from any other node.


```haskell


isConnected :: (Eq a) => ([a], [(a, a)]) -> Bool
isConnected (nodexs, edgexs) =
    let newedgexs = edgexs ++ (map (\(x, y) -> (y, x)) edgexs)
        outxs = subIsConnected (nodexs, newedgexs) (length nodexs)
    in  outxs

subIsConnected :: (Eq a) => ([a], [(a, a)]) -> Int -> Bool
subIsConnected ((fstval:nodexs), edgexs) cmp =
    let outxs = subIsConnected2 edgexs [fstval] fstval cmp
    in cmp == (length . unique $ outxs)

subIsConnected2 :: (Eq a) => [(a, a)] -> [a] -> a -> Int -> [a]
subIsConnected2 xs outxs n cmp
    | length outxs == cmp = outxs
    | otherwise =
        let newxs = filter (\(x, _) -> x == n) xs
        in  if null newxs
            then outxs
            else concat $ map (\(_, x2) -> subIsConnected2 xs (x2:outxs) x2 cmp) newxs


```

## 5\. How the algorithm works

The `spantree2` function explores every possible subset of edges in the original graph
(using backtracking and combinations), and filters those that:


- Include all the original nodes.
- Contain exactly `n − 1` edges (so they can form a tree).
- Are connected (checked using `isConnected`).

The `foldr`-based accumulation step generates all subsets of edges recursively:


```
acc e es = es ++ (map (e:) es)
```

This is a standard pattern for subset generation — each recursive step either includes the edge `e` or skips it.


## 6\. Example

Let’s test it on a small graph:


```haskell

λ> let g = (['a','b','c'], [('a','b'), ('b','c'), ('a','c')])
λ> spantree2 g
[("bac",[('b','c'),('a','c')]),("bac",[('a','b'),('a','c')]),("abc",[('a','b'),('b','c')])]

```

This result lists all possible spanning trees — all subgraphs that include all nodes and no cycles.


## 7\. Building on top of it

Once we have `spantree2`, we can easily define:


- **`is_tree(graph)`** — simply checks whether the graph has `n−1` edges and is connected.
- **`is_connected(graph)`** — as shown above, checks reachability from any starting node.

These definitions reuse the same connectivity logic and filtering conditions from the spanning tree computation.


## 8\. Reflections

- This problem highlights the recursive and declarative power of Haskell — we describe relationships between edges rather than explicitly iterating.
- The combination of `foldr`, `map`, and filtering demonstrates a functional approach to backtracking search.
- It provides an excellent base to explore related algorithms like Kruskal’s and Prim’s minimum spanning trees later on.

## 9\. Wrap-up

Implementing spanning trees in Haskell captures the essence of functional graph algorithms:
expressing search and structure generation through recursion and filtering,
without side effects or mutable state.


Problem 83 serves as both a great introduction to backtracking in Haskell and
a gateway to more advanced topics in algorithmic graph theory.


_Every spanning tree is a minimal structure — and every functional program, a minimal expression of logic._