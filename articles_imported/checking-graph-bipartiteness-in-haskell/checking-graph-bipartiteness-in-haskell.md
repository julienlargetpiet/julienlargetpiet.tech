One of the most elegant problems in graph theory is determining whether a given graph is **bipartite**.
A bipartite graph is one whose nodes can be divided into two disjoint sets such that _no two nodes within the same set are connected by an edge_.


This concept appears everywhere — from scheduling and matching problems to network flow and coloring algorithms.
In this project, I wrote a full Haskell implementation to determine whether any graph is bipartite, even if it’s disconnected.


## 1\. The key idea

If a graph has multiple **connected components** (subgraphs that are not connected to each other),
we can test each subgraph independently.
A disconnected graph is bipartite if and only if _all_ its subgraphs are bipartite.


So the problem splits naturally into two steps:


1. Find all connected components of the graph.
2. Test each connected component for bipartiteness.

Let’s see how this was implemented in Haskell.


## 2\. The code

```haskell


connectedComponents :: (Eq a) => ([a], [(a, a)]) -> [[a]]
connectedComponents (nodexs, edgexs) =
    let newedgexs = edgexs ++ map (\(x, y) -> (y, x)) edgexs
    in subConnectedComponents (zip nodexs (replicate (length nodexs) False))
                              (zip newedgexs (replicate (length newedgexs) False))

subConnectedComponents :: (Eq a) => [(a, Bool)] -> [((a, a), Bool)] -> [[a]]
subConnectedComponents nodexs edgexs = case find (\(_, alrd) -> not alrd) nodexs of
  Just (x, _) ->
    let (outxs, newedgexs) = subConnectedComponents2 [x] edgexs [x]
        newnodexs = map (\(val, alrd) -> if val `elem` outxs then (val, True) else (val, alrd)) nodexs
    in outxs : subConnectedComponents newnodexs newedgexs
  Nothing -> []

subConnectedComponents2 :: (Eq a) => [a] -> [((a, a), Bool)] -> [a] -> ([a], [((a, a), Bool)])
subConnectedComponents2 outxs edgexs trackxs = case find (\((v1, v2), alrd) -> not alrd && v1 == head trackxs) edgexs of
  Just ((v1, v2), _) ->
    let newedgexs = map (\((x1, x2), alrd) ->
                          if (x1 == v1 && x2 == v2) || (x1 == v2 && x2 == v1)
                          then ((x1, x2), True) else ((x1, x2), alrd)) edgexs
        newoutxs = if v2 `elem` outxs then outxs else v2 : outxs
    in subConnectedComponents2 newoutxs newedgexs (v2 : trackxs)
  Nothing -> if length trackxs == 1
             then (outxs, edgexs)
             else subConnectedComponents2 outxs edgexs (tail trackxs)

-- Main bipartite function
bipartite :: (Eq a) => ([a], [(a, a)]) -> Bool
bipartite (nodexs, edgexs) =
    let newnodexs = connectedComponents (nodexs, edgexs)
        graphxs   = constructGraph newnodexs edgexs
    in subBipartite graphxs

constructGraph :: (Eq a) => [[a]] -> [(a, a)] -> [([a], [(a, a)])]
constructGraph [] _ = []
constructGraph (xs:xss) edgexs =
    (xs, filter (\(x, y) -> x `elem` xs || y `elem` xs) edgexs)
    : constructGraph xss edgexs

subBipartite :: (Eq a) => [([a], [(a, a)])] -> Bool
subBipartite [] = True
subBipartite ((nodexs, edgexs):graphxs) =
    let outval = if null edgexs
                 then True
                 else subBipartite2 nodexs [] [] edgexs
    in outval && subBipartite graphxs

subBipartite2 :: (Eq a) => [a] -> [a] -> [a] -> [(a, a)] -> Bool
subBipartite2 [] _ _ _ = True
subBipartite2 (nodeval:nodexs) grp1 grp2 edgexs =
    let outxs = filter (\(val1, val2) -> val1 == nodeval || val2 == nodeval) edgexs
        outxs2 = map (\(val1, val2) -> if val1 == nodeval then val2 else val1) outxs
        outxs2b = filter (\x -> x `elem` grp1 || x `elem` grp2) outxs2
        (isvalid, newgrp1, newgrp2) =
          if null outxs2b && not (nodeval `elem` (grp1 ++ grp2))
          then (True, nodeval:grp1, grp2 ++ outxs2)
          else if head outxs2b `elem` grp1
               then ((all (\x -> not $ x `elem` grp2) outxs2b) && not (nodeval `elem` grp1),
                     grp1 ++ outxs2, nodeval:grp2)
               else ((all (\x -> not $ x `elem` grp1) outxs2b) && not (nodeval `elem` grp2),
                     nodeval:grp1, grp2 ++ outxs2)
    in isvalid && subBipartite2 nodexs newgrp1 newgrp2 edgexs
```

## 3\. Step-by-step explanation

### Step 1 — Splitting the graph

The `connectedComponents` function scans through all nodes and recursively builds each connected subgraph.
It uses a depth-first traversal ( `subConnectedComponents2`) to mark which nodes and edges belong to the same component.


This step is necessary because a disconnected graph must be tested component by component.


### Step 2 — Building subgraphs

The helper `constructGraph` pairs each connected component with its edges, creating smaller, self-contained graphs.
Each of these is tested separately for bipartiteness.


### Step 3 — Checking bipartiteness

The `subBipartite2` function attempts to divide the nodes into two groups ( `grp1` and `grp2`).
It ensures that:


- No node in `grp1` is adjacent to another in `grp1`.
- No node in `grp2` is adjacent to another in `grp2`.

If every connected component satisfies these conditions, the entire graph is bipartite.


## 4\. Example

Let’s test with two graphs — one bipartite, one not:


```haskell

graph89a = ([1,2,3,4,5],[(1,2),(2,3),(1,4),(3,4),(5,2),(5,4)])
λ> bipartite graph89a
True

graph89b = ([1,2,3,4,5],[(1,2),(2,3),(1,3),(1,4),(3,4),(5,2),(5,4)])
λ> bipartite graph89b
False

```

The first graph can be colored using two colors — every edge connects nodes of opposite colors —
while the second graph contains an odd cycle (1–2–3–1), making bipartition impossible.


## 5\. Why this approach is elegant

- It naturally handles disconnected graphs.
- It’s purely functional — no mutable state, just recursion and pattern matching.
- It mirrors theoretical graph reasoning: “Split, analyze, and test per component.”
- It directly implements the _coloring method_ conceptually, but without colors — just two sets.

## 6\. Reflections

This project demonstrates how Haskell can handle even classically imperative graph problems
through recursion, immutability, and clean decomposition of subproblems.


From finding connected components to testing bipartiteness, each step remains declarative and easy to reason about.
The code isn’t just functional — it reflects the mathematical definition of bipartite graphs directly.


_Graph theory meets Haskell’s purity — and the result is both precise and expressive._