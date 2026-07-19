import numpy as np

vls = np.linspace(0, 3, (25 - 3))

vls = np.array([max(0, v - 1) for v in vls])
reds = [ 1 if vl >= 1 else vl % 1 for vl in vls ]

print(vls)

vls = np.array([max(0, v - 1) for v in vls])
greens = [ 1 if vl >= 1 else vl % 1 for vl in vls ]

print(vls)

vls = np.array([max(0, v - 1) for v in vls])
blues = [ 1 if vl >= 1 else vl % 1 for vl in vls ]

print(vls)

blu
