import pandas as pd
import numpy as np

days_mnth = [
    31,  # January
    28,  # February
    31,  # March
    30,  # April
    31,  # May
    30,  # June
    31,  # July
    31,  # August
    30,  # September
    31,  # October
    30,  # November
    31,  # December
]

days_mnth_leap = [
    31,  # January
    29,  # February
    31,  # March
    30,  # April
    31,  # May
    30,  # June
    31,  # July
    31,  # August
    30,  # September
    31,  # October
    30,  # November
    31,  # December
]

days_mnth2 = [
    0,    # Before January
    31,   # Before February
    59,   # Before March
    90,   # Before April
    120,  # Before May
    151,  # Before June
    181,  # Before July
    212,  # Before August
    243,  # Before September
    273,  # Before October
    304,  # Before November
    334,  # Before December
]

days_mnth_leap2 = [
    0,    # Before January
    31,   # Before February
    60,   # Before March
    91,   # Before April
    121,  # Before May
    152,  # Before June
    182,  # Before July
    213,  # Before August
    244,  # Before September
    274,  # Before October
    305,  # Before November
    335,  # Before December
]

TIME_RESOLUTION_MULT_VAL = (
   86_400, #24 * 60 * 60
   3_600,
   60
)

def is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def leap_years_before(year: int) -> int:

    year -= 1

    return year // 4 - year // 100 + year // 400

#EPOCH_YEAR_DAYS = (
#    366 * leap_years_before(1970)
#    + 365 * (1969 - leap_years_before(1970))
#)

#EPOCH_YEAR_DAYS = (
#    365 * 1969 + leap_years_before(1970)
#)

EPOCH_YEAR_DAYS = 719_162

def get_epoch(
    yr: int = 1970,
    mnth: int = 1,
    dy: int = 1,
    hour: int = 0,
    mn: int = 0,
    sec: int = 0,
    millisecond: int = 0,
    microsecond: int = 0,
    nanosecond: int = 0,
    unit: str = "ns",
) -> int:

    if unit not in {"s", "ms", "us", "ns"}:
        raise ValueError("Unit must be 's', 'ms', 'us', or 'ns'")

    if yr < 1:
        raise ValueError("Year must be at least 1")

    if not 1 <= mnth <= 12:
        raise ValueError("Month must be between 1 and 12")

    is_leap_val = is_leap(yr)

    month_days = days_mnth_leap if is_leap_val else days_mnth
    max_day = month_days[mnth - 1]

    if not 1 <= dy <= max_day:
        raise ValueError(f"Day must be between 1 and {max_day}")

    if not 0 <= hour <= 23:
        raise ValueError("Hour must be between 0 and 23")

    if not 0 <= mn <= 59:
        raise ValueError("Minute must be between 0 and 59")

    if not 0 <= sec <= 59:
        raise ValueError("Second must be between 0 and 59")

    if not 0 <= millisecond <= 999:
        raise ValueError("Millisecond must be between 0 and 999")

    if not 0 <= microsecond <= 999:
        raise ValueError("Microsecond must be between 0 and 999")

    if not 0 <= nanosecond <= 999:
        raise ValueError("Nanosecond must be between 0 and 999")

    total_days = 0

    #if yr >= 1970:
    #    for year in range(1970, yr):
    #        total_days += 366 if is_leap(year) else 365
    #else:
    #    for year in range(yr, 1970):
    #        total_days -= 366 if is_leap(year) else 365

    tot_leap_years = leap_years_before(yr)
    #total_days += 366 * tot_leap_years + 365 * (yr - 1 - tot_leap_years) - EPOCH_YEARS_DAYS
    total_days += 365 * (yr - 1) + tot_leap_years - EPOCH_YEAR_DAYS

    mnths_offset = ( days_mnth_leap2 if is_leap_val else days_mnth2 )
    total_days += mnths_offset[mnth - 1]
    
    total_days += dy - 1

    total_seconds = (
        total_days * 24 * 3600
        + hour * 3600
        + mn * 60
        + sec
    )

    #operators = {
    #    "s":  lambda x: x,
    #    "ms": lambda x: x * 1_000 + millisecond,
    #    "us": lambda x: (x * 1_000 + millisecond) * 1_000 + microsecond,
    #    "ns": lambda x: ((x * 1_000 + millisecond) * 1_000 + microsecond) * 1_000 + nanosecond,
    #}

    #return operators[unit](total_seconds)

    if unit == "s":
        return total_seconds

    if unit == "ms":
        return (
            total_seconds * 1_000
            + millisecond
        )
    
    if unit == "us":
        return (
            total_seconds * 1_000_000
            + millisecond * 1_000
            + microsecond
        )
    
    return (
        total_seconds * 1_000_000_000
        + millisecond * 1_000_000
        + microsecond * 1_000
        + nanosecond
    )

def timezone_extractor(s: str) -> str:
    if s.endswith("Z"):
        return s[-1]

    if (
        len(s) >= 6
        and s[-6] in "+-"
        and s[-5:-3].isdigit()
        and s[-3] == ":"
        and s[-2:].isdigit()
    ):

        hour = int(s[-5:-3])
        minute = int(s[-2:])

        if hour <= 23 and minute <= 59:
            return s[-6:]

        raise ValueError("Invalid UTC offset")

    return ""

MLT_TIME = {
             "s": 1,
             "ms": 1_000,
             "us": 1_000_000,
             "ns": 1_000_000_000
           }

UNIT_DIGITS = {
    "s": 0,
    "ms": 3,
    "us": 6,
    "ns": 9,
}

POW10 = (
    1,
    10,
    100,
    1_000,
    10_000,
    100_000,
    1_000_000,
    10_000_000,
    100_000_000,
    1_000_000_000,
)

def get_time_tmz(s: str, 
                      unit: str):
    return (int(s[0:2]) * 3600 + int(s[3:5]) * 60) * MLT_TIME[unit]

def get_time_tmz2(s: str, unit: str) -> int:
    
    try:
        multiplier = MLT_TIME[unit]
    except KeyError as exc:
        raise ValueError(
            "unit must be 's', 'ms', 'us', or 'ns'"
        ) from exc

    if len(s) == 5:
        # HH:MM
        hour = int(s[0:2])
        minute = int(s[3:5])
        second = 0
        fraction = ""

    elif len(s) == 8:
        # HH:MM:SS
        hour = int(s[0:2])
        minute = int(s[3:5])
        second = int(s[6:8])
        fraction = ""

    elif len(s) > 9:
        # HH:MM:SS.fraction
        hour = int(s[0:2])
        minute = int(s[3:5])
        second = int(s[6:8])
        fraction = s[9:]

        if not fraction.isdigit():
            raise ValueError(
                "Fractional seconds must contain only digits"
            )

        if len(fraction) > 9:
            raise ValueError(
                "At most 9 fractional digits are supported"
            )

    else:
        raise ValueError(
            "Expected HH:MM, HH:MM:SS, or HH:MM:SS.fraction"
        )

    if not 0 <= hour <= 23:
        raise ValueError("Hour must be between 0 and 23")

    if not 0 <= minute <= 59:
        raise ValueError("Minute must be between 0 and 59")

    if not 0 <= second <= 59:
        raise ValueError("Second must be between 0 and 59")

    total_seconds = hour * 3600 + minute * 60 + second
    result = total_seconds * multiplier

    if len(fraction) > 9:
        unit_digits = UNIT_DIGITS[unit]

        if len(fraction) > unit_digits:
            raise ValueError(
                f"Unit {unit!r} cannot represent "
                f"{len(fraction)} fractional digits"
            )

        #fraction_in_unit = int(
        #    fraction.ljust(unit_digits, "0")
        #)

        #result += fraction_in_unit
        # Or more performant

        #result += int(fraction) * 10 ** (unit_digit - len(fraction))

        # or even
        result += int(fraction) * POW10[unit_digits - len(fraction)]

    return result

def detect_resolution2(s: str,
                       unit = "ns"):

    if s[0] == " ":
        s = s.lstrip()

    if s[-1] == " ":
        s = s.rstrip()

    tmz = timezone_extractor(s)
  
    tmz_offset = len(tmz)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1
        #tmz_offset_time = sign * get_time_tmz(tmz[1:], unit)
        tmz_offset_time = sign * get_time_tmz2(tmz[1:], unit)
    else:
        tmz_offset_time = 0

    real_len = len(s) - tmz_offset

    if real_len == 4:

        year = int(s)

        scale = 366 if is_leap(year) else 365
        scale *= TIME_RESOLUTION_MULT_VAL[0]
        scale *= MLT_TIME[unit]

        lwr_bnd = get_epoch(year, unit = unit)
        upr_bnd = lwr_bnd + scale - 1

    elif real_len == 7:

        yr_int = int(s[:4])
        mnth_int = int(s[5:real_len])

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")

        scale = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]
        scale *= TIME_RESOLUTION_MULT_VAL[0]
        scale *= MLT_TIME[unit]

        lwr_bnd = get_epoch(yr_int,
                            mnth_int,
                            unit = unit)

        upr_bnd = lwr_bnd + scale - 1

    elif real_len == 10:
        
        yr_int = int(s[:4])
        mnth_int = int(s[5:7])
        dy_int = int(s[8:real_len])

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")
 
        dy_max = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]

        if dy_int < 1 or dy_int > dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")      

        scale = TIME_RESOLUTION_MULT_VAL[0]
        scale *= MLT_TIME[unit]

        lwr_bnd = get_epoch(yr_int,
                            mnth_int,
                            dy_int,
                            unit = unit)

        upr_bnd = lwr_bnd + scale - 1

    elif real_len == 13:

        yr_int = int(s[:4])
        mnth_int = int(s[5:7])
        dy_int = int(s[8:10])
        h_int = int(s[11:real_len])

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")
 
        dy_max = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]

        if dy_int < 1 or dy_int > dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")

        if not 0 <= h_int <= 23:
            raise ValueError("Hour must be between 0 and 23")

        scale = TIME_RESOLUTION_MULT_VAL[1]
        scale *= MLT_TIME[unit] 

        lwr_bnd = get_epoch(yr_int,
                            mnth_int,
                            dy_int,
                            h_int,
                            unit = unit)

        upr_bnd = lwr_bnd + scale - 1

    elif real_len == 16:
                
        yr_int = int(s[:4])
        mnth_int = int(s[5:7])
        dy_int = int(s[8:10])
        h_int = int(s[11:13])
        mn_int = int(s[14:real_len])

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")
 
        dy_max = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]

        if dy_int < 1 or dy_int > dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")

        if not 0 <= h_int <= 23:
            raise ValueError("Hour must be between 0 and 23")

        if not 0 <= mn_int <= 59:
            raise ValueError("Minute must be between 0 and 59")

        scale = TIME_RESOLUTION_MULT_VAL[2]
        scale *= MLT_TIME[unit] 

        lwr_bnd = get_epoch(yr_int,
                            mnth_int,
                            dy_int,
                            h_int,
                            mn_int,
                            unit = unit)

        upr_bnd = lwr_bnd + scale - 1

    elif real_len == 19:

        yr_int = int(s[:4])
        mnth_int = int(s[5:7])
        dy_int = int(s[8:10])
        h_int = int(s[11:13])
        mn_int = int(s[14:16])
        sec_int = int(s[17:real_len])

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")
 
        dy_max = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]

        if dy_int < 1 or dy_int > dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")

        if not 0 <= h_int <= 23:
            raise ValueError("Hour must be between 0 and 23")

        if not 0 <= mn_int <= 59:
            raise ValueError("Minute must be between 0 and 59")

        if not 0 <= sec_int <= 59:
            raise ValueError("Second must be between 0 and 59")

        scale = MLT_TIME[unit] 

        lwr_bnd = get_epoch(yr_int,
                            mnth_int,
                            dy_int,
                            h_int,
                            mn_int,
                            sec_int,
                            unit = unit)

        upr_bnd = lwr_bnd + scale - 1

    elif real_len > 20:
        yr_int = int(s[:4])
        mnth_int = int(s[5:7])
        dy_int = int(s[8:10])
        h_int = int(s[11:13])
        mn_int = int(s[14:16])
        sec_int = int(s[17:19])
        fraction = s[20:real_len]
    
        if not fraction.isdigit():
            raise ValueError(
                "Fractional seconds must contain only digits"
            )
    
        digits = len(fraction)
    
        if digits > 9:
            raise ValueError(
                "At most 9 fractional digits are supported"
            )
    
        if not 1 <= mnth_int <= 12:
            raise ValueError("Month must be between 1 and 12")
    
        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )
    
        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )
    
        if not 0 <= h_int <= 23:
            raise ValueError("Hour must be between 0 and 23")
    
        if not 0 <= mn_int <= 59:
            raise ValueError("Minute must be between 0 and 59")
    
        if not 0 <= sec_int <= 59:
            raise ValueError("Second must be between 0 and 59")
    
        unit_digits = UNIT_DIGITS[unit]
    
        if digits > unit_digits:
            raise ValueError(
                f"Unit {unit!r} cannot represent "
                f"{digits} fractional digits"
            )
    
        scale = POW10[unit_digits - digits]
        fraction_lower = int(fraction) * scale
        fraction_upper = fraction_lower + scale - 1
    
        second_epoch = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )
    
        lwr_bnd = second_epoch + fraction_lower
        upr_bnd = second_epoch + fraction_upper    

    else:
        raise ValueError("Unsupported datetime format")

    return lwr_bnd - tmz_offset_time, upr_bnd - tmz_offset_time

def detect_resolution(s: str):
    
    if len(s) == 4:
        
        lwr_bnd = s + "-01-01" + " " + "00:00:00.000000000"
        upr_bnd = s + "-12-31" + " " + "23:59:59.999999999"

    elif len(s) == 7:

        yr, mnth = s.split("-")
        
        yr_int = int(yr)
        mnth_int = int(mnth)

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")

        lwr_bnd = yr + "-" + mnth + "-01"  + " " +  "00:00:00.000000000"
        upr_bnd = yr + "-" + mnth + "-" + str( days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1] ) + " " + "23:59:59.999999999"

    elif len(s) == 10:
        
        yr, mnth, dy = s.split("-")
        
        yr_int = int(yr)
        mnth_int = int(mnth)
        dy_int = int(dy)

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")
 
        dy_max = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]

        if dy_int < 1 or dy_int > dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")      

        lwr_bnd = yr + "-" + mnth + "-" + dy + " " + "00:00:00.000000000"
        upr_bnd = yr + "-" + mnth + "-" + dy + " " + "23:59:59.999999999"

    elif len(s) == 13:

        yr, mnth, dy = s.split("-")
        dy, h = dy.split(" ")

        yr_int = int(yr)
        mnth_int = int(mnth)
        dy_int = int(dy)
        h_int = int(h)

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")
 
        dy_max = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]

        if dy_int < 1 or dy_int > dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")

        if not 0 <= h_int <= 23:
            raise ValueError("Hour must be between 0 and 23")

        lwr_bnd = yr + "-" + mnth + "-" + dy + " " + h + ":00:00.000000000"
        upr_bnd = yr + "-" + mnth + "-" + dy + " " + h + ":59:59.999999999"

    elif len(s) == 16:
                
        yr, mnth, dy = s.split("-")
        dy, h = dy.split(" ")      
        h, mn = h.split(":")

        yr_int = int(yr)
        mnth_int = int(mnth)
        dy_int = int(dy)
        h_int = int(h)
        mn_int = int(mn)

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")
 
        dy_max = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]

        if dy_int < 1 or dy_int > dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")

        if not 0 <= h_int <= 23:
            raise ValueError("Hour must be between 0 and 23")

        if not 0 <= mn_int <= 59:
            raise ValueError("Minute must be between 0 and 59")

        lwr_bnd = yr + "-" + mnth + "-" + dy + " " + h + ":" + mn + ":00.000000000"
        upr_bnd = yr + "-" + mnth + "-" + dy + " " + h + ":" + mn + ":59.999999999"

    elif len(s) == 19:

        yr, mnth, dy = s.split("-")
        dy, h = dy.split(" ")      
        h, mn, sec = h.split(":")

        yr_int = int(yr)
        mnth_int = int(mnth)
        dy_int = int(dy)
        h_int = int(h)
        mn_int = int(mn)
        sec_int = int(sec)

        if mnth_int < 1 or mnth_int > 12:
            raise ValueError("Month must be between 1 and 12")
 
        dy_max = days_mnth_leap[mnth_int - 1] if is_leap(yr_int) else days_mnth[mnth_int - 1]

        if dy_int < 1 or dy_int > dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")

        if not 0 <= h_int <= 23:
            raise ValueError("Hour must be between 0 and 23")

        if not 0 <= mn_int <= 59:
            raise ValueError("Minute must be between 0 and 59")

        if not 0 <= sec_int <= 59:
            raise ValueError("Second must be between 0 and 59")

        lwr_bnd = yr + "-" + mnth + "-" + dy + " " + h + ":" + mn + ":" + sec + ".000000000"
        upr_bnd = yr + "-" + mnth + "-" + dy + " " + h + ":" + mn + ":" + sec + ".999999999"  

    elif len(s) > 20 and s[19] == ".":
        yr, mnth, dy = s.split("-")
        dy, time_part = dy.split(" ")
        h, mn, sec_fraction = time_part.split(":")
        sec, fraction = sec_fraction.split(".", 1)
    
        if not fraction.isdigit():
            raise ValueError("Fractional seconds must contain only digits")
    
        digits = len(fraction)
    
        yr_int = int(yr)
        mnth_int = int(mnth)
        dy_int = int(dy)
        h_int = int(h)
        mn_int = int(mn)
        sec_int = int(sec)
    
        if not 1 <= mnth_int <= 12:
            raise ValueError("Month must be between 1 and 12")
    
        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )
    
        if not 1 <= dy_int <= dy_max:
            raise ValueError(f"Day must be between 1 and {dy_max}")
    
        if not 0 <= h_int <= 23:
            raise ValueError("Hour must be between 0 and 23")
    
        if not 0 <= mn_int <= 59:
            raise ValueError("Minute must be between 0 and 59")
    
        if not 0 <= sec_int <= 59:
            raise ValueError("Second must be between 0 and 59")
    
        prefix = f"{yr}-{mnth}-{dy} {h}:{mn}:{sec}."
    
        if digits <= 3:
            fraction = fraction.ljust(3, "0")
            lwr_bnd = prefix + fraction + "000000"
            upr_bnd = prefix + fraction + "999999"
    
        elif digits <= 6:
            fraction = fraction.ljust(6, "0")
            lwr_bnd = prefix + fraction + "000"
            upr_bnd = prefix + fraction + "999"
    
        elif digits <= 9:
            fraction = fraction.ljust(9, "0")
            lwr_bnd = prefix + fraction
            upr_bnd = lwr_bnd
    
        else:
            raise ValueError("At most 9 fractional digits are supported")
    
    else:
        raise ValueError("Unsupported datetime format")

    return lwr_bnd, upr_bnd

a, b = detect_resolution("2024")

print(a)

print(b)

print("####")

a, b = detect_resolution("2024-02")

print(a)

print(b)

print("###")

a, b = detect_resolution("2024-02-11")

print(a)

print(b)

print("###")

a, b = detect_resolution("2024-02-11 22")

print(a)

print(b)

print("###")

a, b = detect_resolution("2024-02-11 22:34")

print(a)

print(b)

print("###")

a, b = detect_resolution("2024-02-11 22:34:55")

print(a)

print(b)

print("###")

a, b = detect_resolution("2024-02-11 22:34:55.127")

print(a)

print(b)

print("###")

a, b = detect_resolution("2024-02-11 22:34:55.127128")

print(a)

print(b)

print("###")

a, b = detect_resolution("2024-02-11 22:34:55.127128129")

print(a)

print(b)

assert detect_resolution2("1970") == (
    0,
    get_epoch(
        1970, 12, 31, 23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

assert detect_resolution2("1970-01-01") == (
    0,
    86_400_000_000_000 - 1,
)

assert detect_resolution2(
    "1970-01-01 00:00:00.123",
) == (
    123_000_000,
    123_999_999,
)

assert detect_resolution2(
    "1970-01-01 00:00:00.123456",
) == (
    123_456_000,
    123_456_999,
)

assert detect_resolution2(
    "1970-01-01 00:00:00.123456789",
) == (
    123_456_789,
    123_456_789,
)

base = get_epoch(
    2024, 1, 1, 0, 0, 0, 123,
    unit="ns",
)

one_hour = 3_600_000_000_000

print(f"base: {(base - one_hour, base + one_hour - 999_999)}")

rslt = detect_resolution2(
    "2024-01-01 00:00:00.123+01:00",
    unit = "ns"
) 
print(f"result: {rslt}")

assert detect_resolution2(
    "2024-01-01 00:00:00.123+01:00",
    unit = "ns"
) == (
    base - one_hour,
    base - one_hour + 999_999,
)

assert detect_resolution2(
    "2024-01-01 00:00:00.123-01:00",
    unit="ns",
) == (
    base + one_hour,
    base + one_hour + 999_999,
)

idx = pd.date_range("2024-01-01 12:00:00", 
                    periods = 30, 
                    freq = "6h")


a, b = detect_resolution("2024-01-05")

ser = pd.Series(list(range(30)), index = idx)

serb = ser.loc[a:b]

print(serb)

print(np.shares_memory(ser, serb))

a, b = detect_resolution2("2024-01-05", unit = idx.unit)

idx2a = pd.Index( [ vl for vl in idx if vl.value >= a and vl.value <= b ] )

positions = [ i for i, vl in enumerate(idx.asi8) if vl >= a and vl <= b ]

serc = ser.iloc[positions[0]:positions[-1] + 1]

print("###")

print(positions[0], positions[-1])

print(serc)

print(np.shares_memory(ser, serb))

mn_bnd = np.searchsorted(idx.asi8, a, side = "left")

mx_bnd = np.searchsorted(idx.asi8, b, side = "right")

serc = ser.iloc[mn_bnd:mx_bnd]

print("###")

print(mn_bnd, mx_bnd)

print(serc)

print(np.shares_memory(ser, serb))


#
#print(ser2)

#s1 = idx.get_loc(a)
#s2 = idx.get_loc(b)
#
#print("ok")
#
#s3 = slice(s1.start, s2.stop)
#
#
#print(s3)
#

assert timezone_extractor("2024-01-01 11:12:13 +01:00") == "+01:00"

assert timezone_extractor("2024-01-01 11:12:13 -01:01") == "-01:01"

assert timezone_extractor("2024-01-01 11:12:13 Z") == "Z"




