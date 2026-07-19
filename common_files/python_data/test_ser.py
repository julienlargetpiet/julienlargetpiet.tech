import pandas as pd
import numpy as np

idx = pd.IntervalIndex.from_breaks(
    pd.date_range("2024-01-01", periods=6, freq="D"),
    closed="neither"
)

x = pd.Series(["small", "medium", "large", "xl", "xxl"], index=idx)

x_origin = pd.Series(
    np.random.normal(1, 2.5, 12).clip(1, 5).round()
)

x2 = x_origin.map(lambda v: pd.Timestamp(f"2024-01-{int(v):02d}"))

x3 = x2.map(lambda vl: x[vl])

print(x3)
