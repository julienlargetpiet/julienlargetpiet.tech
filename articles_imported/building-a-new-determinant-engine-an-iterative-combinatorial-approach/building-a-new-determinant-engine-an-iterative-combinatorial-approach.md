One morning, I decided to compute a determinant from scratch — no recursion, no Gaussian elimination,
no library shortcuts. I wanted to understand what really happens behind the determinant and see if it
could be expressed as a purely iterative combinatorial process.


That exploration became part of my C++ library
[Fulgurance](https://github.com/julienlargetpiet/fulgurance/) — a framework for statistics,
linear algebra, and data manipulation.


## Idea: an iterative cofactor traversal (flattening the tree)

In the classic Laplace expansion, computing a determinant means recursively removing one row and one column
until you reach 2×2 minors. Each recursive branch corresponds to a combination of column indices — but recursion
itself isn’t fundamental.


The determinant can be computed _iteratively_ by:


- Enumerating the valid column subsets directly,
- Computing the sign via permutation parity (number of inversions),
- Multiplying the corresponding pivot values and the terminal 2×2 minors.

This effectively **flattens the recursive cofactor tree** into a two-level combinatorial walk.


 

| Concept | Classical Laplace | My Engine |
| --- | --- | --- |
| Traversal | Recursive calls | Iterative enumeration |
| Sign handling | Depth-based alternation | Permutation parity (inversions) |
| Submatrices | Built via recursion | Derived in-place |
| Asymptotic complexity | O(n!) | O(n!) but cache–friendly, zero recursion |






## The core algorithm (C++17)

Below is the heart of the determinant engine — a purely iterative implementation that computes `det(A)` for any square matrix stored in a single column-major vector.

```cpp



// Inside class Matrix<TB> with 1-D column-major storage: rtn_matr[row + nrow * col]

double det() {
    if (nrow != ncol) {
        std::cout << "No det can be calculated for a non-square Matrix\n";
        return 0.0;
    }

    std::vector<int> vec(nrow - 2), mooves_vec(nrow - 2, 0), pos_vec;
    int i, cur_pos;
    std::vector<int> sub_pos, set_pos(nrow);
    for (i = 0; i < nrow; ++i) set_pos[i] = i;
    for (i = 0; i < (int)vec.size(); ++i) vec[i] = i;

    double detval = 0.0;

    auto permutation_parity = [](const std::vector<int>& a, const std::vector<int>& b) -> int {
        std::vector<int> p = a; p.insert(p.end(), b.begin(), b.end());
        int inv = 0;
        for (size_t i = 0; i < p.size(); ++i)
            for (size_t j = i + 1; j < p.size(); ++j)
                if (p[i] > p[j]) ++inv;
        return inv & 1; // 0 even, 1 odd
    };

    // NOTE: assumes helpers diff2, sort_ascout, sort_descout, sub(...) exist in your lib
    while (mooves_vec[0] < nrow) {
        // --- Pivot product ---
        double detval2 = 1.0;
        for (i = 0; i < (int)vec.size(); ++i)
            detval2 *= rtn_matr[vec[i] * nrow + i]; // a[row=vec[i], col=i]

        // --- 2x2 terminal minor using last two columns (ncol-2, ncol-1) ---
        pos_vec = sort_ascout(diff2(set_pos, vec));
        detval2 *= (
            rtn_matr[pos_vec[1] * nrow + (nrow - 1)] * rtn_matr[pos_vec[0] * nrow + (nrow - 2)] -
            rtn_matr[pos_vec[0] * nrow + (nrow - 1)] * rtn_matr[pos_vec[1] * nrow + (nrow - 2)]
        );

        // --- Sign via permutation parity ---
        int sign_par = permutation_parity(vec, pos_vec);
        detval += detval2 * (sign_par ? -1.0 : 1.0);

        // --- Next combination (iterative move logic) ---
        i = (int)vec.size() - 1;
        if (i > 0) {
            while (mooves_vec[i] == nrow - i - 1) {
                if (--i == 0 && mooves_vec[0] == nrow - i - 1)
                    return detval;
            }
        }

        sub_pos = sub(vec.begin(), vec.begin() + i + 1);
        pos_vec = diff2(set_pos, sub_pos);
        pos_vec = sort_descout(pos_vec);

        int cur = pos_vec.back();
        int min_pos = cur;
        while (cur < vec[i]) {
            pos_vec.pop_back();
            if (pos_vec.empty()) break;
            cur = pos_vec.back();
        }
        vec[i] = pos_vec.empty() ? min_pos : cur;
        mooves_vec[i] += 1;

        for (++i; i < (int)vec.size(); ++i) {
            sub_pos = sub(vec.begin(), vec.begin() + i + 1);
            pos_vec = diff2(set_pos, sub_pos);
            vec[i] = *std::min_element(pos_vec.begin(), pos_vec.end());
            mooves_vec[i] = 0;
        }
    }
    return detval;
}

```

## Benchmarks

I benchmarked my implementation against a textbook recursive Laplace expansion and Eigen’s LU decomposition.
All methods are tested on identical random matrices with a fixed seed. Results below are from Arch Linux,
GCC 15.2, `-O3`.


 

| Matrix size | LaplaceRec (ms) | EigenLU (ms) | MyDet (ms) |
| --- | --- | --- | --- |
| 3×3 | 0.0010 | 0.0040 | 0.0024 |
| 4×4 | 0.0013 | 0.0005 | 0.0049 |
| 5×5 | 0.0064 | 0.0005 | 0.0229 |
| 6×6 | 0.0272 | 0.0007 | 0.1485 |
| 7×7 | 0.1858 | 0.0022 | 1.1741 |
| 8×8 | 1.4812 | 0.0012 | 9.8913 |
| 9×9 | 12.321 | 0.0016 | 93.756 |
| 10×10 | 125.567 | 0.0025 | 910.036 |






## Benchmark method (C++17)

The following program generates one random matrix per size, reuses it across all methods, and checks numerical agreement with Eigen within a relative tolerance.

```cpp


#include "fulgurance.h"
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <Eigen/Dense>

// ----------------------------
// Your determinant (1D flat input version)
// ----------------------------
double my_det_flat(const std::vector<double>& flat, int nrow, int ncol) {
    Matrix<double> mat(const_cast<std::vector<double>&>(flat), nrow, ncol);
    return mat.det();
}

// ----------------------------
// Classical Laplace recursive determinant (for validation)
// ----------------------------
double laplace_det(const std::vector<std::vector<double>>& M) {
    int n = (int)M.size();
    if (n == 1) return M[0][0];
    if (n == 2) return M[0][0]*M[1][1] - M[0][1]*M[1][0];

    double det = 0.0;
    for (int col = 0; col < n; ++col) {
        std::vector<std::vector<double>> subM(n-1, std::vector<double>(n-1));
        for (int i = 1; i < n; ++i) {
            int sub_j = 0;
            for (int j = 0; j < n; ++j) {
                if (j == col) continue;
                subM[i-1][sub_j] = M[i][j];
                ++sub_j;
            }
        }
        double sign = ((col % 2) ? -1.0 : 1.0);
        det += sign * M[0][col] * laplace_det(subM);
    }
    return det;
}

// ----------------------------
// Matrix generation utilities
// ----------------------------
std::vector<std::vector<double>> random_matrix_2D(int n) {
    static std::mt19937 rng(42);
    std::uniform_real_distribution<double> dist(-50.0, 50.0);
    std::vector<std::vector<double>> M(n, std::vector<double>(n));
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            M[i][j] = dist(rng);
    return M;
}

// Flatten a 2D matrix into column-major 1D vector
std::vector<double> flatten_col_major(const std::vector<std::vector<double>>& M) {
    int nrow = (int)M.size();
    int ncol = (int)M[0].size();
    std::vector<double> flat;
    flat.reserve(nrow * ncol);
    for (int j = 0; j < ncol; ++j)
        for (int i = 0; i < nrow; ++i)
            flat.push_back(M[i][j]);
    return flat;
}

// ----------------------------
// Benchmark helper
// ----------------------------
template <typename F>
double time_func(F&& f, const std::vector<std::vector<double>>& M,
                 const std::vector<double>& flat, const std::string& name) {
    auto start = std::chrono::high_resolution_clock::now();
    double det = f(M, flat);
    auto end = std::chrono::high_resolution_clock::now();

    double elapsed = std::chrono::duration<double, std::milli>(end - start).count();
    std::cout << name << ": " << elapsed << " ms  | det = " << det << "\n";
    return det;
}

// ----------------------------
// MAIN
// ----------------------------
int main() {
    std::cout << "Benchmarking determinant algorithms\n";
    std::cout << "-----------------------------------\n";

    for (int n = 3; n <= 10; ++n) {
        std::cout << "\nMatrix size: " << n << "x" << n << "\n";

        auto M = random_matrix_2D(n);
        auto flat = flatten_col_major(M);

        double det1 = time_func([](const auto& M, const auto&) {
            return laplace_det(M);
        }, M, flat, "LaplaceRec");

        double det2 = time_func([](const auto& M, const auto&) {
            Eigen::MatrixXd eM(M.size(), M.size());
            for (int i = 0; i < (int)M.size(); i++)
                for (int j = 0; j < (int)M.size(); j++)
                    eM(i,j) = M[i][j];
            return eM.determinant();
        }, M, flat, "EigenLU");

        double det3 = time_func([](const auto&, const auto& flat) {
            int nrow = (int)std::sqrt((double)flat.size());
            return my_det_flat(flat, nrow, nrow);
        }, M, flat, "MyDet (Julien's algo)");

        // Robust relative tolerance check (avoid false mismatches on large magnitudes)
        double diff = std::abs(det3 - det2);
        double tol  = 1e-9 * std::max(std::abs(det2), std::abs(det3));
        if (diff > tol)
            std::cout << "⚠️  Warning: mismatch! Eigen=" << det2
                      << " MyDet=" << det3
                      << " (diff=" << diff << ", tol=" << tol << ")\n";
    }

    return 0;
}

```

### Sample output

```


Benchmarking determinant algorithms
-----------------------------------

Matrix size: 3x3
LaplaceRec: 0.00098 ms  | det = -35221.5
EigenLU: 0.00415 ms  | det = -35221.5
MyDet (Julien's algo): 0.00273 ms  | det = -35221.5

Matrix size: 4x4
LaplaceRec: 0.00124 ms  | det = 2.62367e+06
EigenLU: 0.00045 ms  | det = 2.62367e+06
MyDet (Julien's algo): 0.00493 ms  | det = 2.62367e+06

Matrix size: 5x5
LaplaceRec: 0.00658 ms  | det = -2.7827e+08
EigenLU: 0.00052 ms  | det = -2.7827e+08
MyDet (Julien's algo): 0.022771 ms  | det = -2.7827e+08

Matrix size: 6x6
LaplaceRec: 0.02718 ms  | det = -1.14656e+09
EigenLU: 0.00068 ms  | det = -1.14656e+09
MyDet (Julien's algo): 0.142782 ms  | det = -1.14656e+09

Matrix size: 7x7
LaplaceRec: 0.190832 ms  | det = -5.5291e+10
EigenLU: 0.00232 ms  | det = -5.5291e+10
MyDet (Julien's algo): 1.16233 ms  | det = -5.5291e+10

Matrix size: 8x8
LaplaceRec: 1.47538 ms  | det = 8.04028e+12
EigenLU: 0.00084 ms  | det = 8.04028e+12
MyDet (Julien's algo): 9.88595 ms  | det = 8.04028e+12

Matrix size: 9x9
LaplaceRec: 12.7095 ms  | det = -7.75088e+13
EigenLU: 0.001451 ms  | det = -7.75088e+13
MyDet (Julien's algo): 94.2386 ms  | det = -7.75088e+13

Matrix size: 10x10
LaplaceRec: 125.567 ms  | det = -1.0161e+18
EigenLU: 0.00252 ms  | det = -1.0161e+18
MyDet (Julien's algo): 910.036 ms  | det = -1.0161e+18

```

## Reflections & closing

This determinant engine doesn’t rely on Gaussian elimination or LU decomposition. It walks directly through the
combinatorial structure of the determinant — **flattening** what’s normally a recursive expansion.


It’s a hybrid of cofactor theory and combinatorial traversal:
each iteration represents one “path” through the determinant’s combinatorial space, signed by parity and finalized
through a 2×2 minor.


The engine is included in [Fulgurance](https://github.com/julienlargetpiet/fulgurance/) — my C++ library
for statistics, linear algebra, and data manipulation.


_Sometimes the best way to learn an algorithm is to reinvent it completely._