import pandas as pd
import matplotlib.pyplot as plt
import time, math
import numpy as np
from itertools import product
from collections import defaultdict

xs = list(range(1_000, 5_000_000, 100_000))
ys = []

n_repeats = 1_000

rng = np.random.default_rng(55)

lvls = [ ['A', 'B', 'C'], [1, 2], ['T', 'E'] ]

rep_val = math.prod([ len(x) for x in lvls ])

original_sz = rep_val

codes = []

for pr in lvls:

    sz = len(pr)

    cur_arr = np.arange(0, sz)
    
    cur_arr = np.repeat(cur_arr, np.full(sz, rep_val // sz))

    itr = original_sz // rep_val

    if itr > 1: cur_arr = np.tile(cur_arr, itr)

    codes.append(cur_arr)

    rep_val //= sz

lvls_choice = [x for x in product(*lvls)]

base_val = math.prod([len(x) for x in lvls])
# OR
#base_val = np.array([len(x) for x in levels]).prod()

for n in xs:

    result = None

    hmn = n // base_val
    counts = np.full(base_val, hmn, dtype = np.int32)
    counts[: n % base_val] += 1

    cur_codes = []
    for i in range(len(lvls)):
        cur_codes.append(np.repeat(codes[i], counts))

    idx = pd.MultiIndex(
            levels = lvls,
            codes = cur_codes,
            names = ["g1", "g2", "g3"]
          )

    keys_indices = rng.integers(0, len(lvls_choice), size = n_repeats)
    keys = [lvls_choice[i] for i in keys_indices]

    hsh = defaultdict(list)
    for i, key in enumerate(idx.values):
        hsh[key].append(i)

    print("ok")

    start = time.perf_counter()

    for key in keys:
        result = hsh[key]
        #hsh[key]

    elapsed = time.perf_counter() - start

    ys.append(elapsed / n_repeats)

fig, ax = plt.subplots()

ax.plot(xs, ys, "r*-")
ax.set_xlabel("Index size")
ax.set_ylabel("Average get_loc time")

fig.savefig("measure_multi_index3b2.png")



