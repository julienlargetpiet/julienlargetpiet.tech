import pandas as pd
from typing import Self
import numpy as np

class DatetimeRangeSr:

    def __init__(
        self,
        sr: pd.Series,
        metadata,
    ): 
        match metadata:
            case (a, b, c):
                self.__init1(sr, metadata)
            case (a, b):
                self.__init2(sr, metadata)
            case _:
                raise ValueError("`metadata` must be a tupple of 2 - (start, stop) or 3 (start, stop, step)")

    def __init1(
        self,
        sr: pd.Series,
        metadata: tuple[pd.Timestamp, pd.Timestamp, pd.Timedelta],
    ):
        start, stop, step = metadata

        if not isinstance(start, pd.Timestamp):
            start = pd.Timestamp(start)

        if not isinstance(stop, pd.Timestamp):
            stop = pd.Timestamp(stop)

        if not isinstance(step, pd.Timedelta):
            step = pd.Timedelta(step)

        if step <= pd.Timedelta(0):
            raise ValueError("step must be positive")

        if not start < stop:
            raise ValueError("stop must be higher than start")

        expected_len = (stop - start) // step

        if start + expected_len * step != stop:
            raise ValueError("stop must align exactly with start + n * step")

        if len(sr) != expected_len:
            raise ValueError(
                f"Series length does not match datetime range: "
                f"len(sr)={len(sr)}, expected={expected_len}"
            )

        self.sr = sr.reset_index(drop=True)
        self.start = start
        self.stop = stop
        self.step = step
        self.length = int(expected_len)

    def __init2(
        self,
        sr: pd.Series,
        metadata: tuple[pd.Timestamp, pd.Timestamp],
    ):
        start, stop = metadata

        if not isinstance(start, pd.Timestamp):
            start = pd.Timestamp(start)

        if not isinstance(stop, pd.Timestamp):
            stop = pd.Timestamp(stop)
        
        if not start < stop:
            raise ValueError("stop must be higher than start")

        step = (stop - start) / len(sr)

        expected_len = (stop - start) // step

        if start + expected_len * step != stop:
            raise ValueError("stop must align exactly with start + n * step")

        if len(sr) != expected_len:
            raise ValueError(
                f"Series length does not match datetime range: "
                f"len(sr)={len(sr)}, expected={expected_len}"
            )

        self.sr = sr.reset_index(drop=True)
        self.start = start
        self.stop = stop
        self.step = step
        self.length = int(expected_len)

    def __len__(self):
        return self.length

    def __repr__(self):
        return (
            f"DatetimeRangeSr("
            f"start={self.start!r}, "
            f"stop={self.stop!r}, "
            f"step={self.step!r}, "
            f"length={self.length}"
            f")\n"
            f"{self.sr}"
        )

    def datetime_at(self, i: int) -> pd.Timestamp:
        if i < 0:
            i += self.length

        if i < 0 or i >= self.length:
            raise IndexError("index out of bounds")

        return self.start + i * self.step

    def position_of(self, date: pd.Timestamp) -> int:
        date = pd.Timestamp(date)

        if date < self.start or date >= self.stop:
            raise KeyError("date out of bounds")

        delta = date - self.start

        if delta % self.step != pd.Timedelta(0):
            raise KeyError("date does not match the DatetimeRangeSr step")

        return int(delta // self.step)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.sr.iloc[key]

        if isinstance(key, slice):
            return self._getitem_slice(key)

        date = pd.Timestamp(key)
        idx = self.position_of(date)
        return self.sr.iloc[idx]


    def _normalize_slice(self, key: slice) -> slice:
        if (
            (key.start is None or isinstance(key.start, int))
            and (key.stop is None or isinstance(key.stop, int))
            and (key.step is None or isinstance(key.step, int))
        ):
            return key

        if key.start is None:
            start_pos = 0
        else:
            start_pos = self.position_of(pd.Timestamp(key.start))

        if key.stop is None:
            stop_pos = self.length
        else:
            stop = pd.Timestamp(key.stop)

            if stop > self.stop:
                raise ValueError("stop out of bounds")
            elif stop == self.stop:
                stop_pos = self.length
            else:
                stop_pos = self.position_of(stop)

        if key.step is None:
            slice_step = 1
        elif isinstance(key.step, int):
            slice_step = key.step
        else:
            step = pd.Timedelta(key.step)

            if step <= pd.Timedelta(0):
                raise ValueError("slice step must be positive")

            if step % self.step != pd.Timedelta(0):
                raise ValueError("slice step must be a multiple of the range step")

            slice_step = int(step // self.step)

        return slice(start_pos, stop_pos, slice_step)

    def _getitem_slice(self, key: slice) -> Self:

        key = self._normalize_slice(key)

        start_pos, stop_pos, slice_step = key.indices(self.length)

        if slice_step <= 0:
            raise ValueError("negative or zero slice steps are not supported yet")

        new_sr = self.sr.iloc[key].reset_index(drop=True)

        new_start = self.datetime_at(start_pos)
        new_step = self.step * slice_step
        new_stop = new_start + len(new_sr) * new_step

        return DatetimeRangeSr(
            new_sr,
            metadata=(new_start, new_stop, new_step),
        )

    def to_series_with_datetime_index(self) -> pd.Series:
        idx = pd.date_range(
            start=self.start,
            periods=self.length,
            freq=self.step,
        )

        return pd.Series(self.sr.to_numpy(), index=idx, name=self.sr.name)

    def concat(self, objects: list[Self]) -> Self:
        all_objects = [self] + objects
    
        step = self.step
    
        for obj in all_objects:
            if obj.step != step:
                raise ValueError("cannot concat: all ranges must have the same step")
    
        for a, b in zip(all_objects, all_objects[1:]):
            if a.stop != b.start:
                raise ValueError(
                    "cannot concat: ranges are not contiguous "
                    f"between {a.stop} and {b.start}"
                )
    
        new_sr = pd.concat(
            [obj.sr for obj in all_objects],
            ignore_index=True,
        )
    
        return type(self)(
            new_sr,
            metadata=(self.start, all_objects[-1].stop, step),
        )

    def _lower_bound_pos(self, other: pd.Timestamp) -> int:
        if other <= self.start:
            return 0
    
        if other > self.stop:
            return self.length
    
        delta = other - self.start
        q = delta // self.step
        r = delta % self.step
    
        if r == pd.Timedelta(0):
            return int(q)
    
        return int(q) + 1
    
    
    def _upper_bound_pos(self, other: pd.Timestamp) -> int:
        if other < self.start:
            return 0
    
        if other >= self.stop:
            return self.length
    
        delta = other - self.start
        q = delta // self.step
        r = delta % self.step
    
        return int(q) + 1
    
    
    def _compare_datetime(self, other, op: str):
        other = pd.Timestamp(other)
    
        values = np.zeros(self.length, dtype=bool)
    
        lb = self._lower_bound_pos(other)
        ub = self._upper_bound_pos(other)
    
        match op:
            case "<":
                values[:lb] = True
            case "<=":
                values[:ub] = True
            case ">":
                values[ub:] = True
            case ">=":
                values[lb:] = True
            case "==":
                values[lb:ub] = True
            case "!=":
                values[:] = True
                values[lb:ub] = False
            case _:
                raise ValueError(f"unknown comparison operator: {op}")
    
        return values

    def __lt__(self, other):
        return self._compare_datetime(other, "<")

    def __le__(self, other):
        return self._compare_datetime(other, "<=")
    
    def __eq__(self, other):
        return self._compare_datetime(other, "==")
    
    def __ne__(self, other):
        return self._compare_datetime(other, "!=")
    
    def __ge__(self, other):
        return self._compare_datetime(other, ">=")
    
    def __gt__(self, other):
        return self._compare_datetime(other, ">")


ser = pd.Series([10, 20, 30, 22, 56])

drs = DatetimeRangeSr(
    ser,
    metadata=(
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-06"),
        pd.Timedelta(days=1),
    ),
)

print("###")

print(drs[pd.Timestamp("2024-01-02"):pd.Timestamp("2024-01-05")])

print("###")

print(drs > pd.Timestamp("2024-01-03"))

print("###")

print(drs[1::2])

print("###")


print(drs[1])

ser2 = pd.Series([10, 20, 30, 22, 56] * 2)

drs2 = DatetimeRangeSr(
    ser2,
    metadata=(
        pd.Timestamp("2024-01-06"),
        pd.Timestamp("2024-01-16"),
        pd.Timedelta(days=1),
    ),
)

print(drs.concat([drs2]))

print("##")

drs3 = DatetimeRangeSr(
    ser2,
    metadata=(
        pd.Timestamp("2024-01-06"),
        pd.Timestamp("2024-01-16"),
    ),
)

print(drs3)


