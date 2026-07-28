import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 10
rng = np.random.default_rng(55)

cat_val = np.array([
    "small",
    "medium",
    "large",
    "extra-large",
])

for n in xs:

    print('ok')

    n_categories = len(cat_val)

    counts = np.full(
        n_categories,
        n // n_categories,
        dtype=np.int64,
    )

    counts[: n % n_categories] += 1

    #cats = np.repeat(cat_val, counts)
    #idx = pd.CategoricalIndex(
    #    cats,
    #    categories=cat_val,
    #    ordered=True,
    #)

    codes = np.repeat(
                rng.permutation(np.arange(n_categories, dtype = np.int8)),
                counts
            )
    idx = pd.Categorical.from_codes(
                        codes, 
                        categories = cat_val, 
                        ordered = True
           )
    idx = pd.CategoricalIndex(idx)

    keys = rng.choice(cat_val[counts > 0], size=n_repeats)

    idx.get_loc(keys[0])

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
fig.savefig("measure_cat_index1b.png")



