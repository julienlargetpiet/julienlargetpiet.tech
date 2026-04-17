At the heart of every computer lies a simple truth: everything is binary. Whether you are working with integers, floating-point numbers, or characters, all data is ultimately represented as sequences of 0s and 1s.

To truly understand how computers operate, developers must go beyond high-level abstractions and study how numbers are represented and manipulated at the binary level. This article covers three pillars of low-level computation:

1. **Bitwise operations** (AND, OR, XOR, NOT, shifts).
2. **Signed integer representations** (one’s complement and two’s complement).
3. **Floating-point numbers** (IEEE 754 standard).

## 1\. Bitwise Operations

Bitwise operators act directly on the binary digits of numbers.

### AND (&)

```

1101   (13)
1011   (11)
----
1001   (9)

```

_Use case:_ masking specific bits.

### OR (\|)

```
1101   (13)
1011   (11)
----
1111   (15)

```

_Use case:_ setting specific bits.

### XOR (^)

```

1101   (13)
1011   (11)
----
0110   (6)

```

_Use case:_ toggling bits, cryptographic primitives.

### NOT (~)

```

00001101   (13)
11110010   (interpreted as -14 in signed context)

```

_Use case:_ flipping all bits.

### Shifts

- **Left shift (<<)**: multiply by 2.
- **Right shift (>>)**: divide by 2 (arithmetic vs logical depending on signedness).

```

00001101 (13)
<< 1 → 00011010 (26)
>> 1 → 00000110 (6)

```

## 2\. Signed Integer Representations

Unsigned integers are straightforward: every bit is a power of 2. For example, in 8 bits:

```

00001101 = 13
11111111 = 255

```

But integers can also be negative, and this requires special encoding. Historically, two major approaches existed: **one’s complement** and **two’s complement**.

### One’s Complement Representation

In one’s complement, the negative of a number is obtained by _inverting all the bits_ of its positive form.

```

+13 = 00001101
-13 = 11110010

```

**Problem:** it introduces two zeros:

```

+0 = 00000000
-0 = 11111111

```

This redundancy complicates arithmetic and equality checks, which is why it was eventually abandoned.

### Two’s Complement Representation (modern standard)

Two’s complement solves the zero problem and is now universally used.

1. Write the positive value in binary.
2. Invert all bits.
3. Add 1.

```

+13 = 00001101
invert → 11110010
add 1 → 11110011

```

So:

```

00001101 = +13
11110011 = -13

```

### Value Ranges

- **Unsigned:** 0 → 2^n - 1
- **One’s complement signed:** -(2^(n-1)-1) → +(2^(n-1)-1) (two zeros)
- **Two’s complement signed:** -2^(n-1) → 2^(n-1) - 1

### Comparison Table (4-bit example)

 

| Binary | Unsigned | One’s Complement | Two’s Complement |
| --- | --- | --- | --- |
| 0000 | 0 | +0 | 0 |
| 0001 | 1 | +1 | +1 |
| 0010 | 2 | +2 | +2 |
| 0111 | 7 | +7 | +7 |
| 1000 | 8 | -7 | -8 |
| 1001 | 9 | -6 | -7 |
| 1110 | 14 | -1 | -2 |
| 1111 | 15 | -0 | -1 |






## 3\. Floating-Point Representation: IEEE 754

Integers are simple compared to real numbers like `3.14`. To standardize floating-point arithmetic, computers use the **IEEE 754** standard.

A floating-point number is stored as:

$$
(-1)^{\\text{sign}}
\\times
1.\\text{mantissa}
\\times
2^{\\text{exponent} - \\text{bias}}
$$

### Single Precision (32 bits)

```

[ Sign (1) ] [ Exponent (8) ] [ Mantissa (23) ]

```

Example: `13.25`

```

1101.01 = 1.10101 × 2^3
Sign = 0
Exponent = 3 + 127 = 130 = 10000010
Mantissa = 10101...

```

```

0 10000010 10101000000000000000000

```

### Double Precision (64 bits)

```

[ Sign (1) ] [ Exponent (11) ] [ Mantissa (52) ]

```

- Greater range and precision (≈15 decimal digits vs ≈7 for single precision).
- Default choice in scientific computing.

### Special Values

- `NaN` (Not a Number)
- `+∞` and `-∞`
- Subnormal numbers for very small magnitudes

## Why This Matters

- **Systems programming:** knowing two’s complement prevents overflow errors.
- **Historical insight:** one’s complement explains quirks on early machines.
- **Cryptography:** XOR and shifts are core building blocks.
- **Numerical analysis:** IEEE 754 rounding must be understood to ensure accuracy.
- **Debugging:** raw memory can mean signed int, unsigned int, or float.

## Conclusion

Binary-level operations are the backbone of all computing. Historically, integers could be represented in **one’s complement** (with two zeros, now obsolete) or **two’s complement** (the universal standard today). Floating-point numbers, meanwhile, follow the **IEEE 754** specification, guaranteeing consistency across platforms.

By mastering these representations and operations, developers gain a deeper understanding of how code interacts with hardware — a critical skill for systems programming, cryptography, and scientific computing.

## Further Exploration

To go beyond theory, I’ve built a C++ library from scratch that emulates all these operations — from bitwise logic to number representations. You can explore it here:

[Numero on GitHub](https://github.com/julienlargetpiet/Numero)