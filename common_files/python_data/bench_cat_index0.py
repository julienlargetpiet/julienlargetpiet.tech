import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 100

rng = np.random.default_rng(55)

cat_val = (
           "small", 
           "medium", 
           "large", 
           "extra-large"
           )

for n in xs:

    cats = np.array([])

    hmn1 = n // len(cat_val)

    for cv in cat_val:
        cats = np.concatenate( [cats, np.array( [cv] * hmn1 ) ] )

    hmn1 *= len(cat_val)

    if n - hmn1 > 0:
        cats = np.concatenate([ 
                               cats, 
                               cats[:n - hmn1] 
                              ] 
                              )

    idx = pd.CategoricalIndex(cats, categories = cat_val, ordered=True)
    keys = rng.choice(cat_val[:min(n, len(cat_val))], size = n_repeats)

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

fig.savefig("measure_cat_index0.png")





