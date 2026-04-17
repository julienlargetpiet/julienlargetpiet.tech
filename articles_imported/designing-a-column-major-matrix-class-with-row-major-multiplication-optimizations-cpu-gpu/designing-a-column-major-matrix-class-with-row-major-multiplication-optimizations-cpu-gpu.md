When I designed my C++ `Matrix<T>` class for _[Fulgurance](https://github.com/julienlargetpiet/fulgurance)_, I deliberately chose a
**column-major** memory layout (Fortran/Eigen style). It fits linear algebra conventions
elegantly: columns are contiguous, column vectors are natural, and transposition and determinant
routines fall into place. But for heavy multiplications, CPU caches love _row-major traversal_.
This article explains the architecture, shows why/how I compute multiplications using a
row-major access pattern (while keeping column-major storage), and finishes with a GPU
benchmark using cuBLAS to show how performance scales on modern hardware.

---

## 1) Column-Major Storage in a 1D Vector

The matrix is stored as a flat 1D vector in **column-major** order. Element
`(i, j)` (row `i`, column `j`) lives at index:

```
index = j * nrow + i

```

Example, for the matrix

```
1 4 7
2 5 8
3 6 9

```

the underlying storage is:

```
[1, 2, 3, 4, 5, 6, 7, 8, 9]

```

This layout keeps column operations straightforward and matches many linear algebra texts and libraries.
However, the standard triple-loop matrix multiplication touches memory in _strides_ in column-major,
which can be unfriendly to CPU caches.

---

## 2) Three Multiplication Paths

### 2.1 Standard Column-Major Multiplication ( `mult1` / `mult2`)

These compute the correct result directly in column-major layout. They are simple and correct,
but the innermost loop often performs strided memory accesses, which may stress the cache.

### 2.2 Optimized Single Multiplication ( `mult1_opt` / `mult2_opt`)

Here I compute as if I had a row-major traversal (which is cache-friendly), and at the end I
perform a single `transpose()` to restore column-major orientation for the result. Asymptotically,
both standard and optimized are `O(n^3)` but the optimized version pays an additional `O(n^2)`
transpose pass. For a single multiplication, the gains can be modest because the transpose may cancel some locality benefits.

### 2.3 Chain-Optimized Multiplication ( `mult1_opt_raw` / `mult2_opt_raw`)

For chained products like `A × B × C × ...`, these functions perform all multiplications in the
row-major mindset and **skip** the transpose after each intermediate step. You do **one final transpose at the end**.
This avoids repeated `O(n^2)` passes between steps and lets you stack multiple multiplications with excellent cache locality:

```

  // Chain-optimized: do all in row-major mindset, transpose once at the end
Matrix<double> R = A.mult1_opt_raw(B).mult1_opt_raw(C).mult1_opt_raw(D);
R.transpose(); // final correction back to column-major orientation

```

---

## 3) Why This Is Faster (Especially in Chains)

- **Cache locality:** Row-major style traversal reads contiguous memory; the CPU can prefetch and
   utilize cache lines efficiently. Strided access (common in naive column-major loops) is less cache-friendly.
- **Fewer index recalculations:** Tight inner loops avoid repeated multiplications for indexing; compilers often optimize this aggressively.
- **Chaining advantage:** If you can defer transposes until the very end, you remove repeated `O(n^2)` work and let the `O(n^3)` core dominate with better constants.

In practice, on modern compilers with `-O3 -march=native`, the standard and single-optimized versions
may perform similarly for small/medium sizes, because compilers hoist index arithmetic and
auto-vectorize effectively. The chain-optimized path, however, shines as chains become longer.

---

## 4) CPU Benchmark (Chained Multiplication)

Below is a fair benchmark focusing on chained multiplication of square matrices:
`R = (((A × B) × C) * D) * E`. It compares:

- `mult1` (standard column-major),
- `mult1_opt` (row-major traversal + transpose),
- `mult1_opt_raw` (chain-optimized: no transpose between steps, one at the end).

```cpp




#include <iostream>
#include <vector>
#include <chrono>
#include "fulgurance.h"  // Include your Matrix class

using namespace std;
using namespace std::chrono;

// Utility to fill matrix with sequential numbers or randoms
template <typename T>
Matrix<T> generate_matrix(int n, bool randomize = false) {
    vector<T> data;
    data.reserve(n * n);
    for (int i = 0; i < n * n; ++i)
        data.push_back(randomize ? (rand() % 100) / 10.0 : i % 10 + 1);
    return Matrix<T>(data, n, n);
}

template <typename Func>
double benchmark(Func f, int repeat = 1) {
    auto start = high_resolution_clock::now();
    for (int i = 0; i < repeat; ++i)
        f();
    auto end = high_resolution_clock::now();
    return duration<double, milli>(end - start).count() / repeat;
}

int main() {
    srand(42);

    vector<int> sizes = {100, 200, 400, 800, 2000}; // you can adjust sizes here

    cout << "🚀 Matrix Multiplication Benchmark\n";
    cout << "-----------------------------------\n";
    cout << "Size\tmult1\tmult1_opt\tmult1_opt_raw\n";

    for (int n : sizes) {
        Matrix<double> A = generate_matrix<double>(n, true);
        Matrix<double> B = generate_matrix<double>(n, true);
        Matrix<double> C = generate_matrix<double>(n, true);
        Matrix<double> D = generate_matrix<double>(n, true);
        Matrix<double> E = generate_matrix<double>(n, true);

        // Baseline: mult1
        double t1 = benchmark([&]() {
            Matrix<double> R = A.mult1(B);
            R = R.mult1(C);
            R = R.mult1(D);
            R = R.mult1(E);
        });

        // Optimized (row-major with internal transpose)
        double t2 = benchmark([&]() {
            Matrix<double> R = A.mult1_opt(B);
            R = R.mult1_opt(C);
            R = R.mult1_opt(D);
            R = R.mult1_opt(E);
        });

        // Optimized chainable (no transpose) + final transpose
        double t3 = benchmark([&]() {
            Matrix<double> R = A.mult1_opt_raw(B).mult1_opt_raw(C).mult1_opt_raw(D).mult1_opt_raw(E);
            R.transpose();
        });

        cout << n << "x" << n << "\t"
             << t1 << " ms\t"
             << t2 << " ms\t"
             << t3 << " ms" << endl;
    }

    return 0;
}

```

**Compile (CPU):**

```


  g++ -O3 -march=native -std=c++20 bench_matrix_mult.cpp -o bench_cpu
./bench_cpu

```

In my runs, for sizes up to ~800×800, `mult1`, `mult1_opt`, and `mult1_opt_raw` are within a few percent of each other
(compiler optimizations are very strong). As chains deepen (3+ multiplications), `mult1_opt_raw` may gain clearly since it
avoids transposes between steps. But we should temper that because the standardcolumn major multiplication sees its indices precomputed by the compiler optimizations. So no great differences between these 3.

---

## 5) GPU Acceleration with cuBLAS

Next step: push the same chained multiplications to the GPU using NVIDIA’s cuBLAS.
We’ll compute `R = (((A × B) × C) × D) × E` for multiple sizes. To keep timings fair,
we time only the compute part between `cublasDgemm` calls and a single final synchronization.

### 5.1 GPU Benchmark (Chained A×B×C×D×E)

```cpp


  #include <cublas_v2.h>
#include <cuda_runtime.h>
#include <chrono>
#include <vector>
#include <iostream>

int main() {
    std::vector<int> nvec = {100, 200, 400, 800, 2000};

    for (int n : nvec) {
        // Host matrices (deterministic fillers)
        std::vector<double> A(n*n), B(n*n), C(n*n), D(n*n), E(n*n);
        for (int i = 0; i < n*n; i++) {
            A[i] = i % 10;
            B[i] = (i % 5) * 0.5;
            C[i] = (i % 7) * 0.3;
            D[i] = (i % 9) * 0.2;
            E[i] = (i % 11) * 0.1;
        }

        double *d_A, *d_B, *d_C, *d_D, *d_E, *d_tmp1, *d_tmp2;
        size_t bytes = n * n * sizeof(double);

        // Allocate device buffers (for production, allocate once at max size and reuse)
        cudaMalloc(&d_A, bytes);
        cudaMalloc(&d_B, bytes);
        cudaMalloc(&d_C, bytes);
        cudaMalloc(&d_D, bytes);
        cudaMalloc(&d_E, bytes);
        cudaMalloc(&d_tmp1, bytes);
        cudaMalloc(&d_tmp2, bytes);

        // Upload to GPU
        cudaMemcpy(d_A, A.data(), bytes, cudaMemcpyHostToDevice);
        cudaMemcpy(d_B, B.data(), bytes, cudaMemcpyHostToDevice);
        cudaMemcpy(d_C, C.data(), bytes, cudaMemcpyHostToDevice);
        cudaMemcpy(d_D, D.data(), bytes, cudaMemcpyHostToDevice);
        cudaMemcpy(d_E, E.data(), bytes, cudaMemcpyHostToDevice);

        cublasHandle_t handle;
        cublasCreate(&handle);

        const double alpha = 1.0, beta = 0.0;

        auto start = std::chrono::high_resolution_clock::now();

        // R1 = A * B  → tmp1
        cublasDgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, n, n, n,
                    &alpha, d_B, n, d_A, n, &beta, d_tmp1, n);

        // R2 = R1 * C → tmp2
        cublasDgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, n, n, n,
                    &alpha, d_C, n, d_tmp1, n, &beta, d_tmp2, n);

        // R3 = R2 * D → tmp1
        cublasDgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, n, n, n,
                    &alpha, d_D, n, d_tmp2, n, &beta, d_tmp1, n);

        // R4 = R3 * E → tmp2 (final)
        cublasDgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, n, n, n,
                    &alpha, d_E, n, d_tmp1, n, &beta, d_tmp2, n);

        cudaDeviceSynchronize();
        auto end = std::chrono::high_resolution_clock::now();

        std::cout << "Size " << n << "x" << n << " | GPU time: "
                  << std::chrono::duration<double, std::milli>(end - start).count()
                  << " ms\n";

        cublasDestroy(handle);
        cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
        cudaFree(d_D); cudaFree(d_E);
        cudaFree(d_tmp1); cudaFree(d_tmp2);
    }
}

```

**Compile (GPU, CUDA Toolkit required):**

```


  nvcc -O3 -lcublas -o gpu_bench gpu_bench.cu
./gpu_bench

```

We launch cuBLAS GEMM calls back-to-back in the default stream and synchronize once at the end.
This is optimal for chained multiplications: calls execute in order; we avoid unnecessary CPU blocking.

---

## 6) CPU vs GPU: What the Numbers Look Like

On my setup, I see results in the ballpark of:





| 100×100 | ~2.14 ms | ~2.21 ms | ≈ 1× |
| 200×200 | ~21.7 ms | ~12.3 ms | ≈ 1.8× |
| 400×400 | ~183 ms | ~5.6 ms | ≈ 33× |
| 800×800 | ~1477 ms | ~38 ms | ≈ 39× |
| 2000×2000 | ~24254,435 ms | ~442 ms | ≈ 55× |




For small matrices, GPU overhead (data transfers, kernel launch) dominates and gains are modest.
Once you pass ~400×400, the GPU’s massive parallelism takes over and leaves the CPU behind.

---

## 7) Practical Guidance

- **Single multiplication:** `mult1` or `mult1_opt` are both fine; differences are small.
- **Chained multiplications (3+):** use `mult1_opt_raw` (no transpose between steps) and transpose once at the end.
- **Very large matrices (≥ 1000×1000):** GPU with cuBLAS ( `cublasDgemm`) brings huge speedups.
- **Memory management on GPU:** for benchmark loops, allocate device buffers once at the maximum size and reuse them across sizes to avoid timing malloc/free.
- **Mixed precision:** if acceptable, switch `double` → `float` and `cublasDgemm` → `cublasSgemm` for additional speed.

---

## 8) Takeaways

Choosing a column-major representation provides mathematical clarity and aligns with many libraries.
By computing multiplications with a row-major access pattern, we retain that clarity while exploiting CPU cache locality.
For deep chains, delaying the final transpose yields a clean performance win. And when data sizes grow,
offloading to the GPU via cuBLAS delivers one to two orders of magnitude speedups — all without changing the high-level math.

**Fulgurance** now spans both worlds: a clear, column-major architecture with CPU-friendly row-major computation paths, and a clean bridge to GPU acceleration for large-scale workloads.