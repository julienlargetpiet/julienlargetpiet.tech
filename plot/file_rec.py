import os
import re

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

print(list_files_rec("dataset_parquet3", r".*\.parquet$"))
