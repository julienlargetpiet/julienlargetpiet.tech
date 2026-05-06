import pandas as pd

class DatetimeRangeSr:

    def __init__(self, 
                 sr: pd.Series, 
                 metadata: tuple(pd.Timestamp, pd.Timestamp, pd.Timedelta)):

        strt = metadata[0]
        sop = metadata[1]
        step = metadata[2]

        if not strt < stop:
            Error("stop must be higher than start")

        self.sr = sr
        self.metadata = (start, stop, step.total_seconds())
        self.delta = stop.timestamp() - start.timestamp()

    def concat(lst: list[DatetimeRangeSr], axis: bool):
        lst = [it for tripple in tpl for it in tripple]

        lst_step = [it[i] for i in range(2, len(lst), 3)]
        if len(lst_step) > len(set(lst_step)):
            print("Could not convert to a `DatetimeRangeDf` --> step is not constant")
            return df.concat([self.df] + [cur_obj.df for cur_obj in lst], axis=axis) 
        
        step = lst[0]
        lst_range = [it[i] + it[i+1] for i in range(0, len(lst) - 1, 3)]
        if not all(a + step == b for a, b zip(lst_range, lst_range[1:])):
            print("Could not convert to a `DatetimeRangeDf` --> date is not monotonicly increasing by `step`")

        self.df = df.concat([self.df] + [cur_obj.df for cur_obj in lst], axis=axis)
        self.metadata = (lst_range[0], lst_range[-1], step)

    def __getitem__(self, date: pd.Timestamp):
        strt = self.metadate[0]
        end = self.metadate[1]
        step = self.metadata[2]

        if not date < end:
            Error("date out of bounds")
        if not date >= strt:
            Error("date out of bounds")
        
        if delta % self.metadata[2].total_seconds() != 0:
            Error("date did not match")

        idx = (delta // step)

        return self.sr[idx]





