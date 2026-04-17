![](/assets/common_files/exp.jpg)

**Cherubin** is my C++ library for computing **very large numbers represented as strings**. One of the hardest functions to implement efficiently in this context is the exponential `exp(x)`. A naïve implementation using the Taylor series converges slowly, requires repeated big-number multiplications and divisions, and becomes impractical very quickly.

With `chexp3`, I managed to **dramatically reduce the execution time** of the exponential function by splitting the input into its **integer part** and **fractional part**, and computing them separately. This way, the function avoids huge Taylor expansions and only uses lightweight operations when needed.

## The Optimization Strategy

Here’s the core idea of `chexp3`:

- **Step 1 — Separate integer and fractional parts:**
   The input `x` (as a string) is split into `partint` and `partflt`.
   Example: `x = "12.34"` → `partint = "12"`, `partflt = "34"`.
- **Step 2 — Compute `exp(integer)` by repeated multiplication:**
   The base `e` (~2.7182818) is multiplied by itself `partint` times.
   This avoids unnecessary series expansions and directly builds up the integer power of `e`.
- **Step 3 — Compute `exp(fractional)` with floating-point:**
   The fractional part is converted to a `double`, and `exp()` from the standard library is used.
   This gives a fast and accurate result for the fractional contribution.
- **Step 4 — Combine results:**
   Multiply the two pieces together with Cherubin’s big-number multiplication `multflt2`.


  Final result:


  ```
  exp(x) = exp(integer) × exp(fractional)
  ```


## Why This Works

Instead of expanding everything with a Taylor series (which would require dozens of terms and huge factorial divisions for large `x`), `chexp3` reduces the computation to two much smaller problems:

- A big-number integer loop (multiplying by `e` repeatedly)
- A standard floating-point exponential on a value between 0 and 1

This drastically reduces the number of big-number operations while keeping the result accurate enough for Cherubin’s goals.

## The Implementation

```cpp

std::string chexp3(std::string &x, std::string base = "2.7182818") {
  if (x == "0") return "1";
  // ...
  // Split integer and fractional part
  // Compute exp(integer) via multiplications of base
  // Compute exp(fractional) via double exp()
  // Combine results
}

```

## Results

By using this integer + fractional decomposition, the runtime of `exp(x)` in Cherubin is reduced by an order of magnitude compared to a naïve Taylor expansion. Large inputs that previously took an impractical amount of time can now be computed much faster.

## Conclusion

This optimization shows how mathematical decomposition can turn an otherwise infeasible big-number calculation into a practical one. `chexp3` doesn’t try to compute `exp(x)` purely symbolically with strings — instead, it mixes strategies: string-based multiplications for the integer part, and a fast floating-point exponential for the fractional part.

The result: a vastly faster exponential function inside Cherubin, proving once again that sometimes the best way to handle big numbers is to combine clever math tricks with pragmatic shortcuts.

👉 Check out the full library here: [Cherubin on GitHub](https://github.com/julienlargetpiet/Cherubin)