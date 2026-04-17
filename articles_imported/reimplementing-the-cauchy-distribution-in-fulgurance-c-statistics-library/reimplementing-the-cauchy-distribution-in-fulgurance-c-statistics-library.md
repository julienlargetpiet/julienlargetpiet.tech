![](/assets/common_files/cauchy.gif)

## Introduction

**Fulgurance** is my C++ statistics library where I reimplemented several probability distributions from scratch, including the **Cauchy distribution**. The goal of Fulgurance is to provide flexible statistical tools in modern C++, without relying heavily on external libraries. It’s also a playground to explore how distributions work internally, both mathematically and computationally.

## Why Reimplement Cauchy?

The Cauchy distribution is a well-known heavy-tailed distribution, often used in physics, Bayesian inference, and robustness testing. Unlike the normal distribution, its mean and variance are undefined — which makes it a good candidate to test statistical implementations. Rebuilding it from scratch in C++ was a great exercise in both numerical computation and random number generation.

## The Four Building Blocks

### 1\. `dcauchy` — Density Function

The probability density function (PDF) of the Cauchy distribution is:

$$
f(x) = \\frac{1}{\\text{scale}\\,\\pi\\left(1 + \\left(\\frac{x - \\text{location}}{\\text{scale}}\\right)^2\\right)}
$$

In Fulgurance:

```cpp

std::vector<double> dcauchy(std::vector<double> &x,
                                  double location = 0,
                                  double scale = 1);

```

This returns the probability density values for each element in the vector `x`.

### 2\. `pcauchy` — Cumulative Distribution Function

The cumulative distribution function (CDF) of the Cauchy distribution can be written in closed form using the arctangent. I implemented it as:

```cpp

std::vector<double> pcauchy(std::vector<double> &x,
                                  double location = 0,
                                  double scale = 1,
                                  double step = 0.01);

```

The formula used is:

$$
F(x) = \\frac{1}{\\pi}\\,\\arctan\\!\\left(\\frac{x - \\text{location}}{\\text{scale}}\\right) + \\frac{1}{2}
$$

I also normalize relative to the first value of the input vector, so results can be interpreted as probabilities over the input set.

### 3\. `qcauchy` — Quantile Function

The quantile (inverse CDF) is useful for generating samples or computing thresholds. It is defined as:

$$
Q(p) = \\text{location}
\+ \\text{scale}\\,\\tan\\!\\bigl(\\pi (p - \\tfrac{1}{2})\\bigr)
$$

In Fulgurance:

```cpp

std::vector<double> qcauchy(std::vector<double> &p,
                                  double location = 0,
                                  double scale = 1);

```

It takes a vector of probabilities `p` and returns the corresponding quantile values.

### 4\. `rcauchy` — Random Number Generation

This one was more fun (and a little hacky 😅). I wanted to generate pseudo-random numbers following a Cauchy distribution without relying directly on the standard library’s random engines. So I improvised by using:

- System clock timestamps ( `std::chrono`)
- Modulo arithmetic to get variability
- Short `std::this_thread::sleep_for` calls to add entropy
- The `tan()` transform to map uniform-like values into a Cauchy distribution

The implementation is:

```cpp

std::vector<double> rcauchy(unsigned int n,
                                  double location = 0,
                                  double scale = 1);

```

It generates `n` values distributed approximately like Cauchy( `location`, `scale`).

## Limitations

- `rcauchy` is not a cryptographically secure or statistically rigorous RNG — it’s a custom experiment to simulate randomness.
- For production use, you would normally rely on `std::cauchy_distribution` from `<random>`.
- The goal here was educational: to understand how each component of the distribution is built.

## Conclusion

Reimplementing the Cauchy distribution in **Fulgurance** was both a math refresher and a programming challenge. I now have my own versions of:

- `dcauchy` — density function
- `pcauchy` — cumulative distribution function
- `qcauchy` — quantile function
- `rcauchy` — random number generator

And this is only one example: I’ve implemented **dozens of other statistical laws** in Fulgurance, all available here:

👉 [GitHub Repository: Fulgurance](https://github.com/julienlargetpiet/fulgurance/)

Even though C++ already provides some distributions in `<random>`, reimplementing them from scratch gave me a much deeper understanding of probability distributions, and was a fun addition to Fulgurance.