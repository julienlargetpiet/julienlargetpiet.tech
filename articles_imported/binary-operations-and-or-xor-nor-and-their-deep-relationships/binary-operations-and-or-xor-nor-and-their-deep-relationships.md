Binary operations are the foundation of computation. At the lowest level, everything reduces to simple operations on bits: `true` (1) and `false` (0).

In this article, we explore the core logical operations:

- AND
- OR
- XOR
- NOR
- XAND (XNOR)

We’ll also look at how they relate to each other — and why XOR can be expressed using only NAND-like constructions.

---

## 1\. Basic Definitions

Let’s define the core operations for two boolean values `A` and `B`.



| A | B | AND | OR | XOR | NOR | XAND (XNOR) |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| 0 | 1 | 0 | 1 | 1 | 0 | 0 |
| 1 | 0 | 0 | 1 | 1 | 0 | 0 |
| 1 | 1 | 1 | 1 | 0 | 0 | 1 |




### Intuition

- **AND ( `&&`)** → both must be true
- **OR ( `||`)** → at least one is true
- **XOR ( `!=`)** → exactly one is true
- **NOR ( `!(A || B)`)** → none are true
- **XAND / XNOR ( `!(A != B)`)** → both are equal

---

## 2\. Vectorized Implementations in C++

Here are implementations operating element-wise on boolean vectors:

```cpp


#include &lt;iostream&gt;
#include &lt;vector&gt;
#include &lt;stdexcept&gt;

std::vector&lt;bool&gt; and_n(const std::vector&lt;bool&gt;&amp; vec1,
                const std::vector&lt;bool&gt;&amp; vec2) {

  std::vector&lt;bool&gt; rtn_v(vec1.size());

  if (vec1.size() &gt; vec2.size()) {
    throw std::invalid_argument("vec1 must have same or lower size than vec2");
  };

  for (int i = 0; i &lt; vec1.size(); i += 1) {
    rtn_v[i] = (vec1[i] &amp;&amp; vec2[i]);
  };

  return rtn_v;
}

std::vector&lt;bool&gt; or_n(const std::vector&lt;bool&gt;&amp; vec1,
                const std::vector&lt;bool&gt;&amp; vec2) {

  std::vector&lt;bool&gt; rtn_v(vec1.size());

  if (vec1.size() &gt; vec2.size()) {
    throw std::invalid_argument("vec1 must have same or lower size than vec2");
  };

  for (int i = 0; i &lt; vec1.size(); i += 1) {
    rtn_v[i] = (vec1[i] || vec2[i]);
  };

  return rtn_v;
}

std::vector&lt;bool&gt; nor_n(const std::vector&lt;bool&gt;&amp; vec1,
                const std::vector&lt;bool&gt;&amp; vec2) {

  std::vector&lt;bool&gt; rtn_v(vec1.size());

  if (vec1.size() &gt; vec2.size()) {
    throw std::invalid_argument("vec1 must have same or lower size than vec2");
  };

  for (int i = 0; i &lt; vec1.size(); i += 1) {
    rtn_v[i] = !(vec1[i] || vec2[i]);
  };

  return rtn_v;
}

std::vector&lt;bool&gt; xor_n(const std::vector&lt;bool&gt;&amp; vec1,
                const std::vector&lt;bool&gt;&amp; vec2) {

  std::vector&lt;bool&gt; rtn_v(vec1.size());
  if (vec1.size() &gt; vec2.size()) {
    throw std::invalid_argument("vec1 must have same or lower size than vec2");
  };

  for (int i = 0; i &lt; vec1.size(); i += 1) {
    rtn_v[i] = (vec1[i] != vec2[i]);
  };

  return rtn_v;
}

std::vector&lt;bool&gt; xand_n(const std::vector&lt;bool&gt;&amp; vec1,
                const std::vector&lt;bool&gt;&amp; vec2) {

  std::vector&lt;bool&gt; rtn_v(vec1.size());

  if (vec1.size() &gt; vec2.size()) {
    throw std::invalid_argument("vec1 must have same or lower size than vec2");
  };

  for (int i = 0; i &lt; vec1.size(); i += 1) {
    rtn_v[i] = !(vec1[i] != vec2[i]);
  };

  return rtn_v;
}

int main() {
    return 0;
}


```

---

## 3\. Relationships Between Operations

### 3.1 XOR and XAND

These are perfect opposites:

```text


XAND(A, B) = NOT(XOR(A, B))
XOR(A, B)  = NOT(XAND(A, B))


```

---

### 3.2 NOR as a Universal Gate

NOR is powerful because it can express everything:

```text


NOT(A)     = NOR(A, A)
OR(A, B)   = NOT(NOR(A, B))
AND(A, B)  = NOR(NOT(A), NOT(B))


```

---

### 3.3 XOR Decomposition

XOR can be rewritten using AND, OR, and NOT:

```text


XOR(A, B) = (A AND NOT(B)) OR (NOT(A) AND B)


```

This is the key identity behind its behavior: _difference detection_.

---

## 4\. XOR as a NAND Construction

NAND is known to be **functionally complete**, meaning all logic can be built from it.

XOR can be expressed using only NAND:

```text


Let:
N1 = NAND(A, B)
N2 = NAND(A, N1)
N3 = NAND(B, N1)

XOR(A, B) = NAND(N2, N3)


```

This is why XOR is sometimes described as a _structured NAND composition_.

---

## 5\. Conceptual Insight

- **AND / OR** → aggregation operations
- **XOR** → _difference detector_
- **XAND** → _equality detector_
- **NOR / NAND** → _universal building blocks_

The deeper idea:

> XOR is not just another operator — it encodes _change_, _mismatch_, and _information_.

This is why XOR appears everywhere:

- cryptography
- hashing
- parity checks
- diffing algorithms

---

## 6\. Memo Technique

Start from `AND` and `OR`.

Negate those operations so we got `NAND` and `NOR`

Now one last thing you jus need to know one of the following:

- `XOR` -\> A != B
- `XAND` -\> A == B

And now negate again one or the other to obtain its "opposite" wether `XAND` or `XOR`

You just have to know 3 expressions, everything else is negation!

(N stands for Negation and `XAND` and `XOR` are true "opposite" :))

- XOR -> difference pattern
- XAND -> equality pattern

## 7\. Final Perspective

All boolean logic collapses into a small set of primitives. Among them:

- NAND and NOR → _construction tools_
- XOR → _information extractor_

And your C++ implementations reflect this beautifully:

- `!=` → XOR
- `!( != )` → XAND
- `!( || )` → NOR

Minimal syntax, maximum meaning.