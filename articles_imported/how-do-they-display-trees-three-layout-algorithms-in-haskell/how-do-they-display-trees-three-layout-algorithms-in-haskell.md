![](/assets/common_files/tree1.jpg)

![](/assets/common_files/tree2.jpg)

![](/assets/common_files/tree3.jpg)

When you visualize data structures in a GUI — such as decision trees, syntax trees, or even neural networks —
one key algorithmic problem hides behind the scenes:
**How do you determine where to draw each node?**

Many libraries in higher-level languages (like Python’s data science tools or visualization frameworks)
rely on carefully designed _tree layout algorithms_ to assign 2D coordinates to nodes.
Problems **64 to 66** from the [99 Haskell Problems](https://wiki.haskell.org/99_questions/60_to_69)
explore exactly that: how to compute node coordinates for different layout styles.


In this article, we’ll go through three classic methods of visualizing trees —
each one balancing symmetry, spacing, and readability differently.


## 1\. Layout Algorithm \#1 — Inorder Positioning (Problem 64)

The first method assigns each node’s position based on two simple rules:


- `x(v)` equals the position of node `v` in an **inorder traversal**.
- `y(v)` equals the **depth** of the node in the tree.

This gives a clean and logically spaced tree.
The resulting layout is compact but not necessarily symmetrical.


```haskell


layout :: (MyTree Char) -> [(Char, (Int, Int))]
layout tree = subLayout tree 0 0 [] 0

subLayout :: (MyTree Char) -> Int -> Int
             -> [(Char, (Int, Int))] -> Int -> [(Char, (Int, Int))]
subLayout MyEmpty _ _ xs _ = xs
subLayout (MyNode x l r) depth pos xs lastright =
    let newpos = subCountNodes l
        newdepth = depth + 1
        lval   = subLayout l newdepth newpos ((x, (newpos + lastright, newdepth)):xs) lastright
        rval   = subLayout r newdepth (pos + newpos) [] (lastright + newpos)
    in lval ++ rval

subCountNodes :: (MyTree Char) -> Int
subCountNodes MyEmpty = 1
subCountNodes (MyNode _ l r) = (subCountNodes l) + (subCountNodes r)
```

Each node’s `x`-coordinate reflects its inorder order, while `y` represents its depth.
This approach is simple and deterministic.


## 2\. Layout Algorithm \#2 — Fixed Spacing by Depth (Problem 65)

The second approach improves symmetry by maintaining a **fixed horizontal distance**
between nodes at the same depth level.


Each level of the tree is assigned a spacing that depends on the maximum tree depth,
ensuring visual balance across the entire layout.


```haskell


layout2 :: (MyTree Char) -> [(Char, (Int, Int))]
layout2 tree =
    let maxdepth = findMaxDepthBinaryTree2 tree
    in subLayout2 tree maxdepth 0 0 False False

subLayout2 :: (MyTree Char) -> Int -> Int ->
                Int -> Bool -> Bool -> [(Char, (Int, Int))]
subLayout2 MyEmpty _ _ _ _ _ = []
subLayout2 (MyNode x l r) maxdepth depth lastright fromright alrd =
    let newdepth = depth + 1
        topval   = (2 ^ (maxdepth - newdepth) `div` 2)
        val = if not fromright
              then if not alrd
                   then (spaceCalc l (maxdepth - newdepth) 1) + topval
                   else lastright + (spaceCalc l (maxdepth - newdepth) 1)
              else lastright + (2 ^ (maxdepth - newdepth))
        newlastright = if not fromright
                       then lastright
                       else val - topval
    in [(x, (val, newdepth))] ++
       (subLayout2 l maxdepth newdepth newlastright False alrd) ++
       (subLayout2 r maxdepth newdepth val True True)

spaceCalc :: (MyTree Char) -> Int -> Int -> Int
spaceCalc MyEmpty _ _ = 0
spaceCalc (MyNode _ MyEmpty _) _ n2 = n2
spaceCalc (MyNode x l r) n n2 =
    (spaceCalc l (n - 1) (n2 + 2^n `div` 4))
```

Here, each level’s horizontal distance halves as we go deeper into the tree,
resulting in a beautifully symmetric diagram.


## 3\. Layout Algorithm \#3 — Compact Symmetrical Layout (Problem 66)

The third method is the most sophisticated.
It aims for a **very compact layout** while maintaining
perfect symmetry for every subtree.


The algorithm computes the minimum spacing required to pack subtrees together as tightly as possible without overlap.


```haskell


layout3 :: (MyTree Char) -> [(Char, (Int, Int))]
layout3 tree = subLayout3a tree [] 0 0 False False 0

subLayout3a :: (MyTree Char) -> [(Char, (Int, Int))] ->
                Int -> Int -> Bool -> Bool -> Int -> [(Char, (Int, Int))]
subLayout3a MyEmpty xs _ _ _ _ _ = xs
subLayout3a (MyNode x l r) xs depth lastright fromright alrd lastval =
    let val = if not alrd
              then subLayout3Preb (MyNode x l r) + 1
              else if fromright
                   then lastright + lastval
                   else lastright - lastval
        newdepth = depth + 1
        newlastval = subLayout3b (MyNode x l r)
    in subLayout3a l ((x, (val, newdepth)):xs) newdepth val False alrd newlastval
       ++ subLayout3a r [] newdepth val True True newlastval

subLayout3b :: (MyTree Char) -> Int
subLayout3b (MyNode _ _ MyEmpty) = 1
subLayout3b (MyNode _ MyEmpty _) = 1
subLayout3b (MyNode _ l r) =
    (min (subLayout3bLeft l 1) (subLayout3bRight r 1))

subLayout3bRight :: (MyTree Char) -> Int -> Int
subLayout3bRight (MyNode _ MyEmpty _) n = n
subLayout3bRight (MyNode _ l _) n = subLayout3bRight l (n + 1)

subLayout3bLeft :: (MyTree Char) -> Int -> Int
subLayout3bLeft (MyNode _ _ MyEmpty) n = n
subLayout3bLeft (MyNode _ _ r) n = subLayout3bLeft r (n + 1)
```

This layout tries to make each node’s children perfectly symmetrical with respect to their parent,
resulting in a tree that feels more natural and balanced.


The key insight of this algorithm lies in how it determines the **horizontal gap** between
two subtrees: it counts how many _right branches_ exist within the left subtree,
and how many _left branches_ exist within the right subtree.
The minimal distance between the two subtrees is then based on these counts —
ensuring that both sides expand just enough to prevent overlap,
while preserving perfect symmetry around the parent node.


In effect, the algorithm measures how deeply each subtree “leans” toward the center
and adjusts the spacing dynamically.
This gives a highly compact yet harmonious layout —
a remarkable balance between geometry and recursion.


## 4\. Comparing the Three Layouts

Each of the three algorithms serves a different goal:


- **Layout 1**: Simple and based on _inorder traversal_. Great for conceptual clarity.
- **Layout 2**: Enforces _level-based symmetry_ — ideal for balanced trees.
- **Layout 3**: Strives for _compactness_ and _aesthetically pleasing proportions_.

These same principles underlie many real-world visualization algorithms,
from data science dashboards to compilers’ syntax tree renderers.


## 5\. Reflections

- Even though this topic looks graphical, it’s deeply algorithmic and mathematical.
- Haskell’s recursive pattern matching expresses these coordinate computations naturally and elegantly.
- These problems are not only beautiful — they teach how structure and geometry meet in algorithm design.

## 6\. Understanding the Geometry Behind All Three Layouts

All three algorithms — even though they differ in style and compactness — rely on the same geometric foundation:
each level of depth in the tree scales horizontally according to a power of two.


The horizontal offset at depth `d` is proportional to `2^(maxDepth - d)`.
This means that every time we move one level deeper, the spacing between nodes halves.
Intuitively, the root has the broadest space to distribute its children,
and each subsequent level refines that spacing, creating a visually balanced structure.


When the algorithm traverses the tree to the **right child**,
the new node’s coordinate is computed relative to the _last node from which the traversal went right_.
In other words, each “right move” inherits its horizontal offset from the previous branching point,
ensuring that sibling subtrees never overlap and stay aligned within their respective regions.


This recursive propagation of spacing and relative positioning is what gives the layouts their internal consistency:
it preserves symmetry in the second algorithm, compactness in the third,
and logical ordering in the first.


From a geometric perspective, the `2^n` pattern defines a kind of “binary grid” under the tree,
and each node simply occupies one cell in that exponentially shrinking coordinate space.


## 7\. Which layout do you prefer?

Personally, I find the third layout algorithm fascinating — it produces a dense,
symmetrical, and intuitive representation of the tree structure.
But depending on the application (for example, decision trees, file explorers, or phylogenetic trees),
each layout may have its strengths.


_From abstract recursion to geometric harmony — Haskell shows how code can quite literally draw meaning._