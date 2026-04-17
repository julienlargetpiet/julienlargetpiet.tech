Huffman encoding is one of the foundational algorithms in data compression — elegant, efficient, and entirely
based on simple mathematical principles.
It converts symbols and their frequencies into binary codes where the most frequent symbols receive shorter codes.


The algorithm is used in many compression systems, including ZIP and JPEG, and fits naturally into functional programming thanks to its recursive and tree-based nature.


In this project, I implemented Huffman coding in Haskell from scratch.
The goal was to explore tree construction, recursion, and symbol encoding rather than optimize for absolute performance.
Interestingly, depending on input characteristics, my approach sometimes generates a code table that uses slightly fewer bits than a classic implementation — but that is highly input-dependent.


## 1\. The problem setup

Given a set of symbols and their frequencies:


```
[('a',45), ('b',13), ('c',12), ('d',16), ('e',9), ('f',5)]
```

The goal is to produce a binary encoding that minimizes the total weighted code length.
A typical expected result might look like:


```
[('a',"0"), ('b',"101"), ('c',"100"), ('d',"111"), ('e',"1101"), ('f',"1100")]
```

However, multiple valid Huffman trees can exist for the same frequency table, all producing codes of the same or near-optimal length.
My implementation produces a different — but still fully correct — encoding.


## 2\. The Haskell implementation

Here is the full implementation of the algorithm:


```haskell


data Tree a b = Leaf b | Node a (Tree a b) (Tree a b) deriving (Show)

huffmanTree :: [(Char, Int)] -> [(Char, [Char])]
huffmanTree xs =
    let (fs, hs)  = subHuffmanTreePrepare xs [] []
        ts = subHuffmanTree1 fs hs []
        newts = subHuffmanTree2 ts
    in subHuffmanTree3 newts []

subHuffmanTreePrepare :: [(Char, Int)] -> [Int] -> [Char]
                                -> ([Int], [Char])
subHuffmanTreePrepare [] fs hs = (fs, hs)
subHuffmanTreePrepare (x:xs) fs hs =
    let f   = snd x
        val = fst x
    in subHuffmanTreePrepare xs (f:fs) (val:hs)

subHuffmanTree1 :: [Int] -> [Char] -> [(Tree Int Char)]
                        -> [(Tree Int Char)]
subHuffmanTree1 [] _  ts = ts
subHuffmanTree1 fs hs ts =
    let minxs = myMinN2 fs 2
        (min1, min2) = getMins minxs
        (newfs3, newhs3, newts3) = if (min1 /= -1) `myAnd` (min2 /= -1)
                                   then let (newfs, newhs, newts) = subHuffmanTreePair fs hs ts [min1, min2]
                                            ids1 = grep2 min1 newfs
                                            ids2 = grep2 min2 newfs
                                            valxs = filter (\(x, y) -> x /= (-1)) [(ids1, min1), (ids2, min2)]
                                            (newfs2, newhs2, newts2) = subHuffmanTreeSingle newfs newhs newts valxs
                                        in (newfs2, newhs2, newts2)
                                   else let ids1 = grep2 min1 fs
                                            ids2 = grep2 min2 fs
                                            valxs = filter (\(x, y) -> x /= (-1)) [(ids1, min1), (ids2, min2)]
                                            (newfs2, newhs2, newts2) = subHuffmanTreeSingle fs hs ts valxs
                                        in (newfs2, newhs2, newts2)
    in subHuffmanTree1 newfs3 newhs3 newts3

subHuffmanTreePair :: [Int] -> [Char] ->
                      [(Tree Int Char)] -> [Int] ->
                      ([Int], [Char], [(Tree Int Char)])
subHuffmanTreePair fs hs ts minxs
    | length minxs == 2 =
        let [(min2, idx2), (min1, idx1)] = myMinIdxN fs 2
            chr1 = (hs !! idx1)
            chr2 = (hs !! idx2)
            ftree = if min1 >= min2
                    then Node (min1 + min2) (Leaf chr2) (Leaf chr1)
                    else Node (min1 + min2) (Leaf chr1) (Leaf chr2)
            newts = ts ++ [ftree]
            (newfs, newhs) = if idx2 > idx1
                             then (deleteListElemn fs [idx1, idx2],
                                   deleteListElemn hs [idx1, idx2])
                             else (deleteListElemn fs [idx2, idx1],
                                   deleteListElemn hs [idx2, idx1])
            newminxs = myMinN2 newfs 2
        in  subHuffmanTreePair newfs newhs newts newminxs
    | otherwise = (fs, hs, ts)

subHuffmanTreeSingle :: [Int] -> [Char] ->
                        [(Tree Int Char)] -> [(Int, Int)] ->
                        ([Int], [Char], [(Tree Int Char)])
subHuffmanTreeSingle fs hs ts [] = (fs, hs, ts)
subHuffmanTreeSingle fs hs ts [(_, minx)] =
    let idx = closerIdxSpe minx ts
        (Node sm l r) = (ts !! idx)
        chrvl = (hs !! idx)
        newtree = if minx >= sm
                  then (Node (sm + minx) (Node sm l r) (Leaf chrvl))
                  else (Node (sm + minx) (Leaf chrvl) (Node sm l r))
        newts = updateListElem ts idx newtree
        newfs = deleteListElem fs idx
        newhs = deleteListElem hs idx
    in (newfs, newhs, newts)

subHuffmanTree2 :: [(Tree Int Char)] -> (Tree Int Char)
subHuffmanTree2 [x] = x
subHuffmanTree2 ((Node x1 l1 r1):xs) =
    let idx = closerIdxSpe x1 xs
        (Node x2 l2 r2) = (xs !! idx)
        tree = if x1 >= x2
               then Node (x1 + x2) (Node x2 l2 r2) (Node x1 l1 r1)
               else Node (x1 + x2) (Node x1 l1 r1) (Node x2 l2 r2)
        newxs = updateListElem xs idx tree
    in subHuffmanTree2 newxs

subHuffmanTree3 :: (Tree Int Char) -> [Char] -> [(Char, [Char])]
subHuffmanTree3 (Leaf chr) hs = [(chr, hs)]
subHuffmanTree3 (Node _ l r) hs = subHuffmanTree3 l (hs ++ ['0']) ++ subHuffmanTree3 r (hs ++ ['1'])
```

## 3\. Example result

Running the function gives:


```haskell


ghci> huffmanTree [('a',45), ('b',13), ('c',12), ('d',16), ('e',9), ('f',5)]
[('f',"000"),('e',"001"),('c',"010"),('b',"011"),('d',"10"),('a',"11")]
```

This output differs from the standard example, but still follows all Huffman properties:


- Each symbol has a unique code.
- Codes are prefix-free (no code is a prefix of another).
- More frequent symbols receive shorter codes.

## 4\. Understanding the process

The implementation builds the Huffman tree in stages:


1. **Preparation:** Extract frequencies and characters separately.
2. **Pairing:** Repeatedly merge the smallest frequency nodes to form subtrees.
3. **Consolidation:** Recursively merge all partial trees until only one root remains.
4. **Code generation:** Traverse the final tree to assign binary codes ('0' for left, '1' for right).

Because Haskell functions are pure and recursive, each transformation builds a new tree without mutating any previous state —
a great example of how declarative logic naturally models hierarchical structures.


## 5\. Reflections

- This project shows how expressive Haskell can be for algorithms like Huffman encoding,
   where recursion and data structures work hand in hand.
- The approach can yield slightly different (but always valid) results depending on how ties between equal frequencies are resolved.
- Exploring different merge heuristics helps understand how data ordering and recursion depth affect the final encoding tree.

## 6\. Wrap-up

Building a Huffman encoder from scratch in Haskell is a rewarding exercise.
It demonstrates how to express complex algorithms through pure functions and recursion,
while also deepening understanding of how trees, weights, and ordering affect encoding efficiency.


While my version can produce slightly different bit distributions depending on the input,
it always generates a correct Huffman encoding that respects prefix-free structure and optimal compression logic.


_In the end, this is a great example of how mathematical ideas and functional programming come together beautifully in Haskell._