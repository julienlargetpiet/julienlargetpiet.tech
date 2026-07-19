import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys1 = []
ys2 = []

n_repeats = 10_000

rng = np.random.default_rng(55)

for n in xs:

    steps = rng.integers(1, 5, size = n)

    idx = pd.Index(np.cumsum(steps))
    keys = rng.choice(idx.to_numpy(), size = n_repeats)

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys1.append(elapsed / n_repeats)

for n in xs:
    
    idx = pd.Index(rng.permutation(n))
    keys = np.random.randint(0, n, size = n_repeats)

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

fig.savefig("measure0b.png")





