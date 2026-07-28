import numpy as np
from itertools import product
import math

lvls = [ ['A', 'B', 'C'], [1, 2], ['T', 'E'] ]

rep_val = math.prod([ len(x) for x in lvls ])

original_sz = rep_val

codes = []

#for pr in lvls:
#
#    sz = len(pr)
#
#    cur_arr = np.arange(0, sz)
#    
#    print("####")
#
#    cur_arr = np.repeat(cur_arr, np.full(sz, rep_val // sz))
#
#    print(cur_arr)
#
#    itr = original_sz // rep_val
#
#    if itr > 0: cur_arr = np.tile(cur_arr, itr)
#
#    codes.append(cur_arr)
#
#    rep_val //= sz

for pr in lvls:

    sz = len(pr)

    cur_arr = np.empty(original_sz, 0)

    cur_sz = rep_val // sz

    for i in range(sz): 
        cur_arr[i * cur_sz : (i + 1) * cur_sz] = i

    itr = original_sz // rep_val

    if itr > 1:
        for i in range(1, itr):
            cur_arr[i * rep_val : (i + 1) * rep_val] = cur_arr[0:rep_val]

    codes.append(cur_arr)

    rep_val //= sz

print(codes)



