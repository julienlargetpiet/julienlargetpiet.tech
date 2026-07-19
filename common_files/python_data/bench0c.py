import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 10_000

rng = np.random.default_rng(55)

for n in xs:

    steps = rng.integers(1, 5, size = n / 3)

    

    idx = pd.Index(np.cumsum(steps))
    keys = rng.choice(idx.to_numpy(), size = n_repeats)

    idx.get_loc(keys[0])

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure0.png")
