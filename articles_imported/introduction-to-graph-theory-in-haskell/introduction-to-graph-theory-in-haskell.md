Graph theory is one of the most fascinating areas of computer science and mathematics,
forming the foundation for countless real-world applications: from social networks
and routing systems to dependency trees in compilers.


When learning Haskell, I was first introduced to graph theory through the
[99 Haskell Problems](https://wiki.haskell.org/index.php?title=99_questions/80_to_89) —
a collection of exercises that gradually expose you to elegant and expressive functional patterns.
Problem 81, in particular, focuses on **finding all acyclic paths between two nodes in a directed graph**.


## 1\. The challenge

The problem is simple to state:


> Given two nodes `a` and `b` in a directed graph,
>  return all possible acyclic paths from `a` to `b`.

For example:


```haskell

λ> paths 1 4 [(1,2),(2,3),(1,3),(3,4),(4,2),(5,6)]
[[1,2,3,4],[1,3,4]]

λ> paths 2 6 [(1,2),(2,3),(1,3),(3,4),(4,2),(5,6)]
[]

```

## 2\. Representing a graph in Haskell

Before diving into the implementation, let’s discuss how to represent a graph.
A very common and practical way is to define it as a tuple:


```
([individual nodes], [(starting node, ending node)])
```

This allows you to clearly separate the **nodes** (the elements or points in your graph)
from the **edges** (the directional connections between them).


For example, a small directed graph could be defined as:


```haskell

myGraph :: ([Char], [(Char, Char)])
myGraph = (['1','2','3','4','5','6'], [('1','2'),('2','3'),('1','3'),('3','4'),('4','2'),('5','6')])

```

However, in our exercise, we only need the list of edges.
So we’ll use the simplified version:


```haskell

myGraph :: [(Int, Int)]
myGraph = [(1,2), (2,3), (1,3), (3,4), (4,2), (5,6)]

```

## 3\. Finding paths between nodes

The function `path` below computes all possible paths between two nodes,
while avoiding cycles by not revisiting nodes already present in the path.


```haskell


path :: (Eq a) => a -> a -> [(a, a)] -> [[a]]
path n1 n2 xs = subPath n1 n2 xs []

subPath :: (Eq a) => a -> a -> [(a, a)] -> [a] -> [[a]]
subPath n1 n2 xs outxs
    | n1 /= n2 =
        let newxs = filter (\(val1, _) -> val1 == n1) xs
        in if not . null $ newxs
           then concat $ map (\(_, newn1) -> subPath newn1 n2 xs (outxs ++ [n1])) newxs
           else []
    | otherwise = [outxs ++ [n2]]


```

## 4\. How it works

The algorithm uses recursion to explore every possible path starting from `n1`:


1. For each edge that starts with `n1`, it recursively explores the destination node.
2. At each step, the current node is added to the output path `outxs`.
3. If we reach the target node `n2`, we add the completed path to the result list.
4. When there are no more outgoing edges from the current node, recursion stops for that branch.

The function collects all such paths using `concat` over the recursive results of each possible next step.


### Example step-by-step

Consider `path 1 4 [(1,2),(2,3),(1,3),(3,4),(4,2),(5,6)]`:


- Starting at `1`, we have two choices: go to `2` or `3`.
- Following `1 → 2`, we continue to `3`, and then to `4`.
- Following `1 → 3`, we go directly to `4`.

The function finds both paths:


```
[[1,2,3,4],[1,3,4]]
```

## 5\. Why this representation works well in Haskell

Haskell’s type system makes graph representation clean and precise:


- You can store all nodes in one list, and all edges in another: `([nodes], [(start, end)])`.
- Pattern matching and recursion make traversal intuitive — especially for depth-first searches like this one.
- Because data is immutable, you never risk modifying the graph accidentally while exploring it.

## 6\. Extending this approach

From this simple recursive model, you can easily extend the algorithm to handle:


- **Weighted graphs** — by associating a cost with each edge.
- **Undirected graphs** — by storing each edge twice, e.g., `(a,b)` and `(b,a)`.
- **Cycle detection** — by keeping track of visited nodes.
- **Shortest paths** — by integrating Dijkstra or A\* algorithms on top of this representation.

## 7\. Wrap-up

This small exercise, originally from the 99 Haskell Problems, is a perfect entry point into graph theory using functional programming.
It demonstrates how recursive decomposition and immutability can express graph traversal elegantly and safely.


In Haskell, graphs are just data — and traversing them becomes an act of pure mathematical reasoning.


_That’s the beauty of functional programming applied to graph theory._