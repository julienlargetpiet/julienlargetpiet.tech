import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

xs = list(range(1_000, 2_000_000, 100_000))
ys = []

n_repeats = 10_000

rng = np.random.default_rng(55)

for n in xs:
    
    idx = pd.Index(rng.permutation(n))
    keys = np.random.randint(0, n, size = n_repeats)

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure2b.png")
