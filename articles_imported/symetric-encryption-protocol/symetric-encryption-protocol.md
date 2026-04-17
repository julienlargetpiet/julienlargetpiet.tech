## Introduction

**How i've implemented an original symetric encryption protocol with combinatorial mathematics**

 [repo](https://github.com/julienlargetpiet/minos_cipher)

Or download on this website as zip:

[zip](/assets/common_files/minos_cipher.zip)

It starts with this formula:

`n! / ((n-k)! * k!)`

It tells how many of k elements combinations can be created in a set of length `n`.

For example, if we have: `[1, 1, 0]`

We notice that the set has a length of 3 there are 2 elements inside. The possible combinations are:

- `[1, 1, 0]`
- `[1, 0, 1]`
- `[0, 1, 1]`

It is intuitively made (easy for a set of length 3), but what tells the formula?

`3! / ((3 - 2)! * 2!) = 6 / (1 * 2) = 3`

We get the number of combinations.

Won't be cool to have an algorithm returning the combinations for k elements inside a set of length `n`?

Well, where to begin? I've spent a lot of time trying to find an algorithm just by watching the combinations of `1` and `0` but found nothing for a set of length `n`.

It's easy to find an algorithm for `[1, 1, 0]`

For example, the last `1` permutes itself to the next element until the end of the set, then same thing for the penultimate, etcetera. But when `n` increases, it made me lose my mind.

I needed another point of view.

Wait, if we represent a table for each compute of `k` among `n`?

Bingo!

Look at that:

A row for an element and the table column number is given by the length of the set. Numbers are the indices of each element in the set.

2 rules must be established to find an algorithm returning all the possible combinations of `k` among `n`.

We don't want an element overlapping another one.

We don't want that a combination be the same as another one.

Indeed, if the first `k` is at the index `3`, the second at the index `2` and the last one at the index `1`

It(s the same thing as having `k1` at the index `1`, `k2` at the index `2` and `k3` at the index `3`. We'll just have:

`[1, 1, 1, 0, 0, 0]`

To respect these conditions, i made sure that when `ki` arrives at the end of the set, i ask to `ki-1` to shift by to the next index, if itself is at its maximum index, we repeat.

When the last `k` is at its maximum index `+ 1`, we stop the algorithm.

You can find the algorithm here and an example with `5` among 9 `9`.

[repo](https://github.com/julienlargetpiet/fulgurance#all_comb)

**How this allow us to cipher data?**

Let's take the following sentence `"Hello World!"` (original right ?)

First, we will convert into binary all its letters, `7 bits` by letter will be enough.

It gives us that:

`
100100011001011101100110110011011110100000101011111011111110010110110011001000100001
`

It looks like combinations of `k` among `n` right ?

We have `n` = number of characters (including space) \* `7 bits` = 12 \* 7 = 84 et k = 45 (number of 1)

Now we'll find the number of iterations for `n = 84 ` and `k = 45`, gives us the combination with the algorithm we talked about.

Let's call this number `X`

Now what we can do is to cipher the sentence as `84`, since it is `n`. Then the 2 decryption keys are `k = 45` and `X`.

**How to decipher?**

We know that we want a set of length `n` with `k` elements with an iteration number equal to `X` according to the established algorithm. So, we get:

`
100100011001011101100110110011011110100000101011111011111110010110110011001000100001
`

Then we convert from binary to characters.

In practice it takes too musch time to cipher and decipher all i one, so we cut the sentence converted in binairy into blocks of `21` or `28` bits, then we proceed the same way to decipher. Notice that we'll have different decryption keys for each block.

The more the block size increases, the more we increase the "strength" of the cipher, but also the compute time.

For example, for `21 bits`, the number of combinations is the sum of `k = 0` to `k = 21`

`
(n!) / ((n-k)!*k!)
`

The best i found is with `21 bits` block size where it took 1 to 2 milliseconds to cipher and decipher the example sentence. `2 097 151` is the number of combinations.

Voilà!