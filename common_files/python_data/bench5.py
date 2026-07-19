import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = [[]] * (25 - 3)

n_repeats = 10

rng = np.random.default_rng(55)

#DISTINCT_INDICES = rng.permutation(np.arange(3, 25))

DISTINCT_INDICES = np.arange(3, 25)[::-1]

for CNT in range(0, 25 - 3, 1):

    DISTINCT_INDEX = DISTINCT_INDICES[CNT]

    for n in xs:
    
        steps = rng.integers(0, DISTINCT_INDEX, size = n)
        idx = pd.Index(steps)
    
        keys = rng.choice(steps, size = n_repeats)
    
        idx.get_loc(keys[0])
    
        start = time.perf_counter()
    
        for key in keys:
            idx.get_loc(key)
    
        elapsed = time.perf_counter() - start
    
        ys[CNT] = np.append(ys[CNT], (elapsed / n_repeats))

fig, ax = plt.subplots()

vls = np.linspace(0, 1, (25 - 3))

reds = vls

greens = vls
greens = np.roll(greens, len(greens) // 2)

blues = vls

#colors = plt.colormaps["turbo"]( np.linspace(0, 1, (25 - 3)) )

for i in range(0, 25 - 3, 1):
    ax.plot(xs, 
            ys[i], 
            marker = "*", 
            linestyle = "-",
            color = (reds[i], greens[i], blues[i]),
            label = f"{DISTINCT_INDICES[i]}")

ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")
ax.legend()

fig.savefig("measure5d.png")






