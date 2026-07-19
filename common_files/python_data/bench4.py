import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys1 = []
ys2 = []

n_repeats = 100

rng = np.random.default_rng(55)

DISTINCT_INDEX = 6

for n in xs:

    hmn1 = n // 3
    counts = np.full(DISTINCT_INDEX,
                     hmn1, 
                     dtype = np.int32)
    counts[: n % DISTINCT_INDEX] += 1
    steps = np.arange(DISTINCT_INDEX)
    idx = pd.Index(np.repeat(steps, counts))

    keys = rng.choice(steps, size = n_repeats)

    idx.get_loc(keys[0])

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys1.append(elapsed / n_repeats)

print("ok")

for n in xs:
   
    vals = rng.permutation(DISTINCT_INDEX)
    hmn1 = n // DISTINCT_INDEX
    counts = np.full(DISTINCT_INDEX,
                     hmn1, 
                     dtype = np.int32)
    counts[: n % DISTINCT_INDEX] += 1
    idx = pd.Index(np.repeat(vals, counts))
    keys = rng.choice(vals, size = n_repeats)

    idx.get_loc(keys[0])

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys2.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys1, "r*-", label = "Monotonic Index")
ax.plot(xs, ys2, "b*-", label = "Shuffled index")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")
ax.legend()

fig.savefig("measure4.png")




