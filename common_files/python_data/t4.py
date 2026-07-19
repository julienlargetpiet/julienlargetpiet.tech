import numpy as np
from itertools import product
import math

lvls = [ ['A', 'B', 'C'], [1, 2], ['T', 'E'] ]

rep_val = math.prod([ len(x) for x in lvls ])

original_sz = rep_val

codes = []

for pr in lvls:

    sz = len(pr)

    cur_arr = np.arange(0, sz)
    
    print("####")

    cur_arr = np.repeat(cur_arr, np.full(sz, rep_val // sz))

    print(cur_arr)

    itr = original_sz // rep_val

    if itr > 0: cur_arr = np.tile(cur_arr, itr)

    codes.append(cur_arr)

    rep_val //= sz

print(codes)
