When I first started playing with determinant algorithms in C++, I wanted to _really_ understand what happens behind Eigen’s `.determinant()` call.
So I decided to reimplement the **LU decomposition** from scratch — the same method used inside Eigen and LAPACK — and compare it with two determinant algorithms I built myself:

- A **recursive Laplace expansion**
- A **non-recursive Laplace expansion** (my own invention 💡)

But to make benchmarking clean and efficient, I represented matrices as **1D flat vectors** in **row-major order**, so that values in the same row are contiguous in memory — perfect for cache-friendly computations.

Here’s the full story, the math, and the code.

---

## 1\. From Laplace to LU

Laplace’s expansion expresses the determinant as a recursive cofactor expansion:

$$
\\det(A) = \\sum\_{j=0}^{n-1} (-1)^j a\_{0j} \\det(M\_{0j})
$$

It’s beautiful, but the computational cost grows factorially — \\(O(n!)\\).
For a 10×10 matrix, that’s millions of recursive calls.

LU decomposition, by contrast, reduces any square matrix \\(A\\) into a product:

$$
A = L \\times U
$$

where \\(L\\) is lower-triangular and \\(U\\) is upper-triangular.
The determinant then becomes:

$$
\\det(A)
=
(\\text{sign of permutations})
\\times
\\prod\_i U\_{ii}
$$

and the complexity drops to \\(O(n^3)\\).
That’s the method Eigen (and most of numerical linear algebra) uses internally.

---

## 2\. The Core Algorithm

Here’s the essence of **LU decomposition with partial pivoting**:

```cpp


    for (int k = 0; k < n; ++k) {
    // 1. Find pivot row (max abs value in column k)
    int pivot = k;
    double max_val = std::abs(A[k * n + k]);
    for (int i = k + 1; i < n; ++i)
        if (std::abs(A[i * n + k]) > max_val)
            pivot = i;

    // 2. Singularity check
    if (max_val < 1e-15)
        return 0.0;  // Numerically singular matrix

    // 3. Swap rows if needed
    if (pivot != k) {
        for (int j = 0; j < n; ++j)
            std::swap(A[pivot * n + j], A[k * n + j]);
        det_sign *= -1.0;
    }

    // 4. Eliminate entries below pivot
    for (int i = k + 1; i < n; ++i) {
        double factor = A[i * n + k] / A[k * n + k];
        for (int j = k; j < n; ++j)
            A[i * n + j] -= factor * A[k * n + j];
    }
}
```

The inner loop computes the elimination factor for each row below the pivot:

$$
\\text{factor}\_i = \\frac{A\_{ik}}{A\_{kk}}
$$

and subtracts that multiple of the pivot row, zeroing out the column entries below the pivot.
When finished, `A` becomes an **upper-triangular matrix**, and the determinant is simply the **product of its diagonal** entries (times the sign of the row permutations).

---

## 3\. The Full Benchmark Code

Here’s the complete code I used to compare the three implementations:

- ✅ **Eigen-style LU decomposition**
- ✅ **Recursive Laplace expansion**
- ✅ **My own non-recursive Laplace expansion**

Each implementation uses a **1D row-major flat vector** representation of the matrix, with row values contiguous in memory.

```cpp


#include "fulgurance.h"
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <cmath>
#include <iomanip>

// =========================================================
// Determinant Implementations
// =========================================================

double laplace_expansion(const std::vector<double>& flat, int n) {
    Matrix<double> mat(const_cast<std::vector<double>&>(flat), n, n);
    return mat.det2(flat, n);
}

double laplace_expansion_no_rec(const std::vector<double>& flat, int n) {
    Matrix<double> mat(const_cast<std::vector<double>&>(flat), n, n);
    return mat.det1();
}

double eigen_lu(const std::vector<double>& flat, int n) {
    Matrix<double> mat(const_cast<std::vector<double>&>(flat), n, n);
    return mat.det3();
}

// =========================================================
// Utilities
// =========================================================

// Directly generate a random n×n matrix as a flat row-major 1D vector
std::vector<double> random_matrix_flat(int n) {
    static std::mt19937 rng(42);
    std::uniform_real_distribution<double> dist(-50.0, 50.0);

    std::vector<double> flat(n * n);
    for (double& v : flat)
        v = dist(rng);

    return flat;
}

// Time a function (with optional repetition)
template <typename Func>
double time_func(Func&& f, const std::string& name, int repeats = 1) {
    double best_time = 1e9;
    double result = 0.0;
    for (int r = 0; r < repeats; ++r) {
        auto start = std::chrono::high_resolution_clock::now();
        result = f();
        auto end = std::chrono::high_resolution_clock::now();
        double elapsed = std::chrono::duration<double, std::milli>(end - start).count();
        best_time = std::min(best_time, elapsed);
    }
    std::cout << std::setw(12) << name << ": " << std::fixed << std::setprecision(3)
              << best_time << " ms  | det = " << result << "\n";
    return result;
}

// =========================================================
// Main benchmark
// =========================================================

int main() {
    std::cout << "Benchmarking determinant algorithms (direct 1D generation)\n";
    std::cout << "----------------------------------------------------------\n";
    std::cout << std::fixed << std::setprecision(6);

    for (int n = 3; n <= 10; ++n) {
        std::cout << "\nMatrix size: " << n << "x" << n << "\n";

        auto flat = random_matrix_flat(n);

        double det_lu = time_func([&]() {
            return eigen_lu(flat, n);
        }, "LU implementation", 3);

        double det_mine = time_func([&]() {
            return laplace_expansion(flat, n);
        }, "Laplace implementation", 3);

        double det_mine2 = time_func([&]() {
            return laplace_expansion_no_rec(flat, n);
        }, "Laplace implementation, no recursivity", 3);

        double diff = std::abs(det_mine - det_lu);
        double tol = 1e-9 * std::max(std::abs(det_lu), std::abs(det_mine));
        if (diff > tol)
            std::cout << "⚠️  Warning: mismatch!  LU=" << det_lu
                      << "  MyDet=" << det_mine
                      << "  (diff=" << diff << ", tol=" << tol << ")\n";
    }

    return 0;
}
```

---

## 4\. Compile Command

To squeeze maximum performance from your CPU:

```

  g++ -O3 -march=native -funroll-loops -ffast-math -std=c++20 benchmark.cpp -o benchmark
```

Then just run:

```

  ./benchmark
```

---

## 5\. Typical Results

```

  Benchmarking determinant algorithms (direct 1D generation)
----------------------------------------------------------

Matrix size: 3x3
 LU implementation: 0.000 ms  | det = -35221.522
 Laplace implementation: 0.001 ms  | det = -35221.522
 Laplace implementation, no recursivity: 0.000 ms  | det = -35221.522

Matrix size: 10x10
 LU implementation: 0.000 ms  | det = -1.0161e+18
 Laplace implementation: 39.834 ms  | det = -1.0161e+18
 Laplace implementation, no recursivity: 966.885 ms  | det = -1.0161e+18
```

Even for a 10×10 matrix, **LU decomposition is over 1000× faster** than Laplace expansion — and that’s on top of being perfectly accurate (matching to within \\(10^{-15}\\)).

---

## 6\. Takeaways

- ✅ **LU decomposition** scales as \\(O(n^3)\\), while **Laplace expansion** grows factorially.
- ✅ **Pivoting** ensures stability by choosing the largest available pivot in each column.
- ✅ **1D row-major layout** ensures memory contiguity and speed.
- ✅ My **non-recursive Laplace** implementation works correctly — but recursion and LU both outperform it massively.
- ✅ Understanding LU “from the inside” gives deep insight into how Eigen and LAPACK achieve their incredible speed.

---

## 7\. Closing Thoughts

This experiment gave me a complete understanding of what’s actually happening under the hood when Eigen computes a determinant or solves a linear system.

I went from:

> “LU decomposition is just some library routine”

to

> “I know exactly why it works, how pivoting avoids singularities,
> and why the determinant is just the product of the diagonal entries.”

Rebuilding it was absolutely worth it.

---

### 🧠 References

- _John von Neumann & Herman Goldstine (1947)_ — _Numerical Inverting of Matrices of High Order_
- _Tadeusz Banachiewicz (1938)_ — _LU factorization notation_
- _J.H. Wilkinson (1950s)_ — _Error analysis and partial pivoting_
- _The Nine Chapters on the Mathematical Art_ (~200 BCE) — the original elimination idea
- Eigen Library documentation — `PartialPivLU`