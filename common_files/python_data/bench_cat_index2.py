import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 1_000
rng = np.random.default_rng(55)

cat_val = np.array([
    "small",
    "medium",
    "large",
    "extra-large",
])

for n in xs:

    available_codes = np.arange(min(n, len(cat_val)))
    cats = rng.choice(available_codes, size = n)
    idx = pd.Categorical.from_codes(cats, 
                                    categories = cat_val,
                                    ordered = True
                                   )
    idx = pd.CategoricalIndex(idx)

    keys = rng.choice(cat_val[0:len(available_codes)], size=n_repeats)

    idx.get_loc(keys[0])  # warm-up

    start = time.perf_counter()

    for key in keys:
        idx.get_loc(key)

    elapsed = time.perf_counter() - start
    ys.append(elapsed / len(keys))

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.tight_layout()
fig.savefig("measure_cat_index2.png")



