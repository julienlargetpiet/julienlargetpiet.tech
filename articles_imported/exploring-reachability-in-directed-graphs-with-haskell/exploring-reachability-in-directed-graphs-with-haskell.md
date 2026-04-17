# Exploring Reachability in Directed Graphs with Haskell

Graphs are a natural way to represent systems of connections — from flight networks to dependencies in code or social networks.
In directed graphs, edges have a direction, and not all nodes may be reachable from one another.
This brings up a fascinating question: **From which nodes can we reach all others?**

To explore this, I wrote a Haskell function that recursively discovers all directed paths in a graph,
and identifies the nodes that can reach every other node.


## 1\. The problem

Given a directed graph represented as a pair `([nodes], [(from, to)])`,
we want to:


- Find all traversal paths starting from every node.
- Keep only the nodes that can reach _all others_.

The function should therefore output a list of path groups — one for each fully reachable starting node.


## 2\. The code

```haskell


findDirection :: (Eq a) => ([a], [(a, a)]) -> [[[a]]]
findDirection (nodexs, edgexs) =
    let outxs = subFindDirection (nodexs, edgexs) (length nodexs)
        newoutxs = filter (\(x1, _) -> x1) outxs
    in  map snd newoutxs

subFindDirection :: (Eq a) => ([a], [(a, a)]) -> Int -> [(Bool, [[a]])]
subFindDirection ([], _) _ = []
subFindDirection ((fstval:nodexs), edgexs) cmp =
    let outxs = subFindDirection2 edgexs [fstval] fstval cmp
    in [(cmp == (length . unique . concat $ outxs), outxs)]
       ++ subFindDirection (nodexs, edgexs) cmp

subFindDirection2 :: (Eq a) => [(a, a)] -> [a] -> a -> Int -> [[a]]
subFindDirection2 xs outxs n cmp
    | length outxs == cmp = [outxs]
    | otherwise =
        let newxs = filter (\(x, _) -> x == n) xs
        in  if null newxs
            then [outxs]
            else concat $ map (\(_, x2) ->
                               subFindDirection2 xs (x2:outxs) x2 cmp) newxs


```

## 3\. Understanding how it works

The algorithm performs a **recursive depth-first traversal** from each node in the graph.


### Step 1 — Exploring all paths

The helper `subFindDirection2` recursively follows every outgoing edge `(n, x2)`,
building all possible directed paths:


- If there are no outgoing edges, the path ends.
- Otherwise, we recurse deeper, adding `x2` to the path.

### Step 2 — Checking full reachability

In `subFindDirection`, we check if a node has reached all others:


```
cmp == (length . unique . concat $ outxs)
```

This means the number of unique nodes visited in all paths equals the total number of nodes.
If that’s true, the node is a fully connected origin.


### Step 3 — Filtering results

The main function `findDirection` then keeps only the fully connected nodes and returns
their complete list of traversal paths.


## 4\. Example

Consider this directed graph:


```haskell

nodes = ['a','b','c']
edges = [('a','b'),('b','c'),('a','c')]

```

Calling:


```haskell

findDirection (nodes, edges)

```

Produces:


```

  [[["c","b","a"],["c","a"]]]


```

In plain words:


- Starting from `'a'`, we can reach everyone: `a → b → c` and `a → c`.
- Starting from `'b'` or `'c'`, we can’t reach all nodes.

Therefore, the only “fully connected origin” is `'a'`.


## 5\. Conceptual view

Conceptually, this algorithm builds a kind of **reachability matrix**:


 

| a | ✅ Yes | [a→b→c, a→c] |
| b | ❌ No | [b→c] |
| c | ❌ No | [c] |






The output structure — `[[[a]]]` — groups all paths by origin,
keeping only the nodes that can fully reach others.


## 6\. What makes this Haskell implementation elegant

- It naturally expresses recursive graph traversal with pure functions.
- No mutable state or explicit stacks — recursion itself tracks the traversal path.
- Filtering and mapping make the post-processing phase concise and readable.
- The code is generic over any `Eq` type — not just characters or integers.

## 7\. Reflections

This project is a great example of how recursion in Haskell can model not just tree structures,
but also complex traversals like reachability in graphs.
The algorithm mimics depth-first search but in a purely functional way.


What’s even more interesting is that it does more than just find paths —
it analyzes which nodes are fully connected, a concept that relates to
**strongly connected components** in graph theory.


_From recursion to reachability — Haskell turns abstract graph logic into elegant, declarative exploration._