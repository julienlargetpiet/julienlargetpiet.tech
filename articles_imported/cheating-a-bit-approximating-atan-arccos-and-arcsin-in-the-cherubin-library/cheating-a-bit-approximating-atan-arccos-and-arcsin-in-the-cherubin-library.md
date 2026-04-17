## Introduction

This project is part of my **Cherubin** library — a C++ library for computing **very large numbers represented as strings**. Because Cherubin works outside the world of hardware floats and doubles, I couldn’t just call `std::atan`, `std::asin`, or `std::acos`. Instead, I had to invent approximations that made sense within the string-based arithmetic of Cherubin. ( [GitHub link](https://github.com/julienlargetpiet/Cherubin))

The result is a set of small but clever tricks to approximate inverse trigonometric functions. They’re not mathematically perfect, but they get the job done and are fast enough to work with big numbers.

## Why Approximate?

Standard math libraries are precise and optimized for floats, but Cherubin manipulates numbers as `std::string` or `std::deque`. Re-implementing full Taylor series everywhere would be very slow, so I turned to shortcuts: polynomial fits, hybrid methods, and even a log-based hack for `atan`.

## The Approximation Strategy

### 1\. Approximating `atan(x)`

Like `arccos`, `arctan` can be approximated with a Taylor series expansion, which converges well in the interval \[−0.5, 0.5\]:

$$
\\arctan(x)
=
x
\- \\frac{x^3}{3}
\+ \\frac{x^5}{5}
\- \\frac{x^7}{7}
\+ \\frac{x^9}{9}
\- \\frac{x^{11}}{11}
\+ \\cdots
$$

Within this range, the Taylor expansion gives accurate results. However, outside of \[−0.5, 0.5\], it quickly loses precision and becomes impractical for big-number computations.

To handle values of `x` outside this range, I used a hack based on the logarithm:

$$
\\arctan(x) \\approx -\\,\\frac{1}{\\ln\\!\\left(x - \\tfrac{1}{2}\\right)}
$$

This isn’t mathematically exact, but in Cherubin’s context it worked surprisingly well as a fallback. Combined, the Taylor expansion (for small x) and the log trick (for larger x) cover the full domain with acceptable accuracy.

### 2\. Approximating `arccos(x)`

`arccos` was the most delicate one, so I relied on its Taylor series expansion, which converges for −1 ≤ x ≤ 1:

$$
\\begin{aligned}
\\arccos(x)
&=
\\frac{\\pi}{2}
-
\\sum\_{n=0}^{\\infty}
\\frac{(2n)!}{2^{2n}(n!)^2(2n+1)} \\, x^{2n+1} \\\\[6pt\]
&=
\\frac{\\pi}{2}
-
\\left(
x
+
\\frac{x^3}{2 \\cdot 3}
+
\\frac{1 \\cdot 3 \\cdot x^5}{2 \\cdot 4 \\cdot 5}
+
\\frac{1 \\cdot 3 \\cdot 5 \\cdot x^7}{2 \\cdot 4 \\cdot 6 \\cdot 7}
+
\\cdots
\\right)
\\end{aligned}
$$

This expansion works well across most of the domain. However, for values of `x` in the region `[0.92, 1.0]`, the Taylor series gave poor accuracy. To fix this, I switched to a degree-2 polynomial fit `1 − 0.5x²` in that narrow interval. This piecewise approach produced stable and accurate results across the whole domain.

### 3\. Approximating `arcsin(x)`

This one was actually trivial once `arccos` was implemented, because:

$$
\\arcsin(x) = \\frac{\\pi}{2} - \\arccos(x)
$$

So rather than designing a new approximation, I simply reused the `arccos` logic. This way, the accuracy of `arcsin` directly tracks that of `arccos`, without extra effort.

## Limitations & Tradeoffs

- The `atan` logarithmic hack doesn’t perfectly match the true function, especially for small x. It’s a compromise for speed and simplicity.
- Approximations lose accuracy near boundaries (\|x\| = 1 for `asin`/ `acos`).
- These methods are not suitable for precise scientific applications, but they’re perfectly fine in Cherubin’s context of big-number experimentation.

## Conclusion

Within **Cherubin**, I needed workable approximations of `atan`, `asin`, and `acos` that fit a string-based math framework. By mixing a log trick, a cubic correction, and a piecewise quadratic patch, I ended up with a set of lightweight approximations that keep calculations flowing without getting bogged down in heavy expansions.

They may be “cheats,” but they prove a point: when you leave the comfort zone of floats and doubles, you can still recreate the math you need — with a little creativity 😎.