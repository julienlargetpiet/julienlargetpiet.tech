import pandas as pd
from typing import Self
import numpy as np

class TimedeltaRangeSr:
    def __init__(
        self,
        sr: pd.Series,
        metadata,
    ):
        match metadata:
            case (a, b, c, d):
                _init1(self, sr, metadata)

            case _:
                raise ValueError("`metadata` must be a tupple of 4 - (start, period, unit, step)")

    def _init1(
        self,
        sr: pd.Series,
        metadata: tuple[pd.Timedelta, int, str, pd.Timedelta],
    ):
        start, period, unit, step = metadata

        if not isinstance(start, pd.Timedelta):
            start = pd.to_timedelta(start, unit=unit)

        if not isinstance(step, pd.Timedelta):
            step = pd.to_timedelta(step, unit=unit)

        if not isinstance(period, int):
            period = int(period)

        if len(sr) != period:
            raise ValueError(
                f"Series length does not match datetime range: "
                f"len(sr)={len(sr)}, expected={period}"
            )

        self.sr = sr.reset_index(drop=True)
        self.start = start
        self.period = period
        self.unit = unit
        self.step = step
        self.stop = start + period * step
        self.length = period

    def _init2(
        self,
        sr: pd.Series,
        metadata: tuple[pd.Timedelta, int, str],
    ):
        start, period, unit, step = metadata

        if not isinstance(start, pd.Timedelta):
            start = pd.to_timedelta(start, unit=unit)

        if not isinstance(step, pd.Timedelta):
            step = pd.to_timedelta(step, unit=unit)

        if not isinstance(period, int):
            period = int(period)

        if len(sr) != period:
            raise ValueError(
                f"Series length does not match datetime range: "
                f"len(sr)={len(sr)}, expected={period}"
            )

        self.sr = sr.reset_index(drop=True)
        self.start = start
        self.period = period
        self.unit = unit
        self.step = step
        self.stop = start + period * step
        self.length = period

    def __len__(self):
        return self.length

    def __repr__(self):
        return (
            f"TimedeltaRangeSr("
            f"start={self.start!r}, "
            f"stop={self.stop!r}, "
            f"period={self.period!r}, "
            f"unit={self.unit!r}, "
            f"step={self.step!r}, "
            f"length={self.length}"
            f")\n"
            f"{self.sr}"
        )

    def timedelta_at(self, i: int) -> pd.Timedelta:
        if i < 0:
            i += self.length

        if i < 0 or i >= self.length:
            raise IndexError("index out of bounds")

        return self.start + i * self.step

    def position_of(self, time: pd.Timedelta) -> int:

        if not isinstance(time, pd.Timedelta):
            time = pd.to_timedelta(time, unit=self.unit)

        if time < self.start or time >= self.stop:
            raise KeyError("date out of bounds")

        delta = time - self.start

        if delta % self.step != pd.Timedelta(0):
            raise KeyError("date does not match the TimedeltaRangeSr step")

        return int(delta // self.step)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.sr.iloc[key]

        if isinstance(key, slice):
            return self._getitem_slice(key)

        if not isinstance(key, pd.Timedelta):
            key = pd.to_timedelta(key, unit=unit)

        idx = self.position_of(key)
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
            start_pos = self.position_of(pd.to_timedelta(key.start))

        if key.stop is None:
            stop_pos = self.length
        else:
            stop = pd.to_timedelta(key.stop)

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
            step = pd.to_timedelta(key.step)

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

        new_start = self.timedelta_at(start_pos)
        new_step = self.step * slice_step
        new_period = (self.timedelta_at(stop_pos) - self.step) // new_step

        return TimedeltaRangeSr(
            new_sr,
            metadata=(new_start, 
                      new_period, 
                      self.unit, 
                      new_step),
        )

    def to_series_with_timedelta_index(self) -> pd.Series:
        idx = np.array([ self.start + self.step * i for i in range(self.length) ])

        return pd.Series(self.sr.to_numpy(), index=idx, name=self.sr.name)

    def concat(self, objects: list[Self]) -> Self:

        if not objects:
            raise ValueError("cannot concat an empty list")

        all_objects = [self] + objects

        for a, b in zip(all_objects, objects):

            if a.stop != b.start:
                raise ValueError(
                    "cannot concat: ranges are not contiguous "
                    f"between {a.stop} and {b.start}"
                )

        new_sr = pd.concat(
            [obj.sr for obj in all_objects],
            ignore_index=True,
        )

        return TimedeltaRangeSr(
            new_sr,
            metadata=(self.start, 
                      np.array([cur_obj.length for cur_obj in all_objects]).sum(), 
                      self.unit, 
                      self.step),
        )

    def _lower_bound_pos(self, other: pd.Timedelta) -> int:
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
    
    
    def _upper_bound_pos(self, other: pd.Timedelta) -> int:
        if other < self.start:
            return 0
    
        if other >= self.stop:
            return self.length
    
        delta = other - self.start
        q = delta // self.step
        r = delta % self.step
    
        return int(q) + 1 
    
    def _compare_datetime(self, other, op: str):
        other = pd.Timedelta(other)
    
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

trs = TimedeltaRangeSr(
    ser,
    metadata=(
        pd.Timedelta(0),
        5,
        "D",
        pd.Timedelta(days=2), 
    ),
)

print(trs.to_series_with_timedelta_index())

print(trs.to_series_with_timedelta_index().index)

print("##")

print(trs[pd.Timedelta(days=2)])

print("##")

print(trs.step)

print("##")

print(trs[pd.Timedelta(days=2):pd.Timedelta(days=8):1])

print("##")

print(trs > pd.Timedelta(days=2))

print("##")

ser2 = pd.Series([10, 20, 30, 22, 56] * 2)

print(trs.stop)

trs2 = TimedeltaRangeSr(
    ser2,
    metadata=(
        trs.stop,
        10,
        "D",
        pd.Timedelta(days=2), 
    ),
)

print(trs2.to_series_with_timedelta_index())

print("##")

print(trs.concat([trs2]))



