import pandas as pd
import numpy as np
import os, shutil
from itertools import product
from pathlib import Path
import re
import time

set_country = ["FR", "EN", "ESP"]
set_location = ["A", "B"]

rng = np.random.default_rng(42)

df = pd.DataFrame({
    "country": rng.choice(set_country, 100_000),
    "location": rng.choice(set_location, 100_000),
    "PIB": rng.normal(3, 15, 100_000),
    })

df = df.sort_values("PIB", ascending=False)
df["PIB_bucket"] = (df["PIB"] // 10) * 10

def get_var(path: str, var: str) -> str | None:
    for part in path.split("/"):
        if part.startswith(var + "="):
            return part.split("=", 1)[1]
    return None

def list_files_rec(dr: str, 
                   rgx: str) -> list[str]:
    rtn_lst = []
    pattern = re.compile(rgx)

    try:
        for name in os.listdir(dr):
            cur = os.path.join(dr, name)
            if os.path.isdir(cur) and not os.path.islink(cur):
                rtn_lst.extend(list_files_rec(cur, rgx))
            elif pattern.search(cur):
                rtn_lst.append(cur)
    except PermissionError:
        pass
    return rtn_lst

def list_files_rec2(dr: str, 
                    f_mask,
                    d_mask) -> list[str]:
    rtn_lst = []

    try:
        for name in os.listdir(dr):
            cur = os.path.join(dr, name)
            if os.path.isdir(cur) and not os.path.islink(name) and d_mask(name):
                rtn_lst.extend(list_files_rec2(cur, f_mask, d_mask))
            elif f_mask(cur):
                rtn_lst.append(cur)
    except PermissionError:
        pass
    return rtn_lst

def make_predicates2(df: pd.DataFrame, dct: dict) -> list:
    keys = list(dct.keys())
    all_combinations = product(*(dct[k] for k in keys))

    predicates = []

    for combo in all_combinations:
        mask = pd.Series(True, index=df.index)
        for k, v in zip(keys, combo):
            mask &= (df[k] == v)
        predicates.append(mask)

    return predicates

def get_ids(n: int, lst_nb: list) -> list:
    ids = []
    for base in reversed(lst_nb):
        ids.append(n % base)
        n //= base
    return list(reversed(ids))

def make_predicates(df: pd.DataFrame, 
                    dct: dict) -> list:
    lst = []
    lst_nb = []
    max_value = 1

    for k in dct.keys():
        cur_lst = []
        for vl in dct[k]:
            cur_lst.append(df[k] == vl)
        lst.append(cur_lst)
        lst_nb.append(len(dct[k]))   
        max_value *= len(dct[k])

    rtn_lst = []

    cnt = 0
    while cnt < max_value:
        ids = get_ids(cnt, lst_nb)

        cur_sr = pd.Series(True, index=df.index)

        for i in range(len(ids)):
            cur_sr &= lst[i][ids[i]]   

        rtn_lst.append(cur_sr)         
        cnt += 1

    return rtn_lst

def write_partitions(f: str,
                     df: pd.DataFrame,
                     *,
                     partitions: list,
                     write_method,
                     ext: str) -> None:

    shutil.rmtree(f, ignore_errors=True)
    os.mkdir(f)

    f += "/"
    dct = {}
    max_value = 1
    lst_nb = []
    for cl in partitions:
        cur_unique = df[cl].unique()
        lst_nb.append(len(cur_unique))
        max_value *= len(cur_unique)
        dct[cl] = cur_unique
    lst_predicates = make_predicates(df, dct)
    
    cnt = 0
    while cnt < max_value:
        ids = get_ids(cnt, lst_nb)
        cur_f = f

        for i in range(len(partitions)):
            k = partitions[i]
            cur_f += f"{k}={dct[k][ids[i]]}/"
        os.makedirs(cur_f, exist_ok=True) # equivalent of bash `mkdir -p`

        cur_f += "data" + ext
        cur_df = df[lst_predicates[cnt]]
        write_method(cur_df, cur_f)
        cnt += 1

def write_partitions2(f: str,
                      df: pd.DataFrame,
                      *,
                      partitions: list,
                      write_method,
                      ext: str) -> None:

    shutil.rmtree(f, ignore_errors=True)

    for keys, subdf in df.groupby(partitions):
        if not isinstance(keys, tuple):
            keys = (keys,)

        cur_f = f + "/"
        for k, v in zip(partitions, keys):
            cur_f += f"{k}={v}/"

        os.makedirs(cur_f, exist_ok=True)

        write_method(subdf, cur_f + "data" + ext)

def d_satisfy(f: str, filters: list | None) -> bool:
    for cond in filters: 
        for col, op, val in cond:  
            ok = True
            cur = get_var(f, col)
            if cur is None:
                ok = False
                continue

            try:
                cur = float(cur)
            except:
                pass

            match op:
                case ">":   ok = (cur > val)
                case ">=":  ok = (cur >= val)
                case "=":   ok = (cur == val)
                case "<=":  ok = (cur <= val)
                case "<":   ok = (cur < val)
                case _:     ok = False

            if ok:
                break

        if ok:
            return True

    return False

def f_satisfy(f: str, filters: list | None) -> bool:
    for cond in filters:
        ok = True
        for col, op, val in cond:  
            cur = get_var(f, col)
            if cur is None:
                ok = False
                break

            try:
                cur = float(cur)
            except:
                pass

            match op:
                case ">":   ok &= (cur > val)
                case ">=":  ok &= (cur >= val)
                case "=":   ok &= (cur == val)
                case "<=":  ok &= (cur <= val)
                case "<":   ok &= (cur < val)
                case _:     ok = False

            if not ok:
                break

        if ok:
            return True

    return False

def read_partitions(f: str,
                    *,
                    filters: list | None = [],
                    columns: list | None = None,
                    read_method) -> pd.DataFrame:

    filters = [] if filters is None else filters

    lst_files = list_files_rec2(f, 
                                lambda p: f_satisfy(p, filters),
                                lambda p: d_satisfy(p, filters)
                                )
    if not lst_files:
        return pd.DataFrame()

    #rtn_df = read_method(lst_files[0])
    #for f in lst_files[1:]:
    #    cur_df = read_method(f)
    #    rtn_df = pd.concat([rtn_df, cur_df], axis = 0)
    # or in ONE allocation for the concatenation
    dfs = [read_method(f) for f in lst_files]
    rtn_df = pd.concat(dfs, axis=0)

    return rtn_df

strt = time.time()
#write_partitions("dataset_feather", 
#                 df,
#                 partitions=["country", "PIB_bucket"],
#                 write_method=pd.DataFrame.to_feather,
#                 ext=".feather")

write_partitions2("dataset_feather", 
                  df,
                  partitions=["country", "PIB_bucket"],
                  write_method=pd.DataFrame.to_feather,
                  ext=".feather")

df = read_partitions("dataset_feather",
                     filters=[
                              [
                                ("PIB_bucket", ">=", 10),
                                ("country", "=", "FR"), 
                              ]
                             ],
                     columns = None,
                     read_method = pd.read_feather
)

end = time.time()

print(df)

print(end - strt)




