import pandas as pd
import numpy as np
import datetime
import re
from typing import Callable

x = datetime.datetime.strptime(
                        "January 31, 2024 05:12:33.89 PM +01:00",
                        "%B %d, %Y %I:%M:%S.%f %p %z"
                              )

print(x)

x2 = pd.Period("2024-01-01")

print(x2.start_time)

print(x2.end_time)

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

def is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def leap_years_before(year: int) -> int:

    year -= 1

    return year // 4 - year // 100 + year // 400

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

ABREV_MONTH_ENG = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

FULL_MONTH_ENG = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

ABREV_DAY_ENG1 = {
    "Mon": 1,
    "Tue": 2,
    "Wed": 3,
    "Thu": 4,
    "Fri": 5,
    "Sat": 6,
    "Sun": 7,
}

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

def detect_resolution2_rfc2822(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if len(s) >= 5 and s[3] == ",":
        s = s[5:]

    return detect_resolution2_day_month(s, unit)


def detect_resolution2_month_day(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if not s:
        raise ValueError("Empty datetime string")

    tmz = timezone_extractor(s)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1

        tmz_offset_time = (
            sign * get_time_tmz2(tmz[1:], unit)
        )
    else:
        tmz_offset_time = 0

    if tmz:
        core = s[:-len(tmz)].rstrip()
    else:
        core = s

    real_len = len(core)

    if real_len == 8:
        month_abbrev = core[0:3]
        yr_int = int(core[4:8])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_max,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 11:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 14:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])
        h_int = int(core[12:14])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 17:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 20:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])
        sec_int = int(core[18:20])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            999,
            999,
            999,
            unit,
        )

    elif real_len > 21:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])
        sec_int = int(core[18:20])

        # Position 20 is the fractional separator.
        fraction = core[21:real_len]

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        if not fraction.isdigit():
            raise ValueError(
                "Fractional seconds must contain only digits"
            )

        digits = len(fraction)

        if digits > 9:
            raise ValueError(
                "At most 9 fractional digits are supported"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

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
        raise ValueError(
            "Unsupported abbreviated-month datetime format"
        )

    return (
        lwr_bnd - tmz_offset_time,
        upr_bnd - tmz_offset_time,
    )

def detect_resolution2_month_day_comma_at(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if not s:
        raise ValueError("Empty datetime string")

    tmz = timezone_extractor(s)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1

        tmz_offset_time = (
            sign * get_time_tmz2(tmz[1:], unit)
        )
    else:
        # No timezone or Z.
        tmz_offset_time = 0

    if tmz:
        core = s[:-len(tmz)].rstrip()
    else:
        core = s

    real_len = len(core)

    if real_len == 8:
        month_abbrev = core[0:3]
        yr_int = int(core[4:8])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_max,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 12:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[8:12])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 18:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[8:12])
        h_int = int(core[16:18])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 21:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[8:12])
        h_int = int(core[16:18])
        mn_int = int(core[19:21])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 24:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[8:12])
        h_int = int(core[16:18])
        mn_int = int(core[19:21])
        sec_int = int(core[22:24])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            999,
            999,
            999,
            unit,
        )

    elif real_len > 25:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[8:12])
        h_int = int(core[16:18])
        mn_int = int(core[19:21])
        sec_int = int(core[22:24])

        # Position 24 is the fractional separator.
        fraction = core[25:real_len]

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        if not fraction.isdigit():
            raise ValueError(
                "Fractional seconds must contain only digits"
            )

        digits = len(fraction)

        if digits > 9:
            raise ValueError(
                "At most 9 fractional digits are supported"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

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
        raise ValueError(
            "Unsupported abbreviated-month comma-at datetime format"
        )

    return (
        lwr_bnd - tmz_offset_time,
        upr_bnd - tmz_offset_time,
    )

def detect_resolution2_month_day(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if not s:
        raise ValueError("Empty datetime string")

    tmz = timezone_extractor(s)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1

        tmz_offset_time = (
            sign * get_time_tmz2(tmz[1:], unit)
        )
    else:
        tmz_offset_time = 0

    if tmz:
        core = s[:-len(tmz)].rstrip()
    else:
        core = s

    real_len = len(core)

    if real_len == 8:
        month_abbrev = core[0:3]
        yr_int = int(core[4:8])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_max,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 11:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 14:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])
        h_int = int(core[12:14])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 17:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 20:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])
        sec_int = int(core[18:20])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            999,
            999,
            999,
            unit,
        )

    elif real_len > 21:
        month_abbrev = core[0:3]
        dy_int = int(core[4:6])
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])
        sec_int = int(core[18:20])

        # Position 20 is the fractional separator.
        fraction = core[21:real_len]

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        if not fraction.isdigit():
            raise ValueError(
                "Fractional seconds must contain only digits"
            )

        digits = len(fraction)

        if digits > 9:
            raise ValueError(
                "At most 9 fractional digits are supported"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

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
        raise ValueError(
            "Unsupported abbreviated-month datetime format"
        )

    return (
        lwr_bnd - tmz_offset_time,
        upr_bnd - tmz_offset_time,
    )



def detect_resolution2_day_month(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if not s:
        raise ValueError("Empty datetime string")

    tmz = timezone_extractor(s)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1

        tmz_offset_time = (
            sign * get_time_tmz2(tmz[1:], unit)
        )
    else:
        # No timezone or Z.
        tmz_offset_time = 0

    if tmz:
        core = s[:-len(tmz)].rstrip()
    else:
        core = s

    real_len = len(core)

    if real_len == 8:
        month_abbrev = core[0:3]
        yr_int = int(core[4:8])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_max,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 11:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[7:11])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 14:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[7:11])
        h_int = int(core[12:14])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 17:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 20:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])
        sec_int = int(core[18:20])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            999,
            999,
            999,
            unit,
        )

    elif real_len > 21:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[7:11])
        h_int = int(core[12:14])
        mn_int = int(core[15:17])
        sec_int = int(core[18:20])

        fraction = core[21:real_len]

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        if not fraction.isdigit():
            raise ValueError(
                "Fractional seconds must contain only digits"
            )

        digits = len(fraction)

        if digits > 9:
            raise ValueError(
                "At most 9 fractional digits are supported"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

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
        raise ValueError(
            "Unsupported day-abbreviated-month datetime format"
        )

    return (
        lwr_bnd - tmz_offset_time,
        upr_bnd - tmz_offset_time,
    )

def detect_resolution2_day_month_comma(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if not s:
        raise ValueError("Empty datetime string")

    tmz = timezone_extractor(s)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1

        tmz_offset_time = (
            sign * get_time_tmz2(tmz[1:], unit)
        )
    else:
        tmz_offset_time = 0

    if tmz:
        core = s[:-len(tmz)].rstrip()
    else:
        core = s

    real_len = len(core)

    if real_len == 8:
        month_abbrev = core[0:3]
        yr_int = int(core[4:8])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_max,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 12:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[8:12])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 15:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[8:12])
        h_int = int(core[13:15])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 18:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[8:12])
        h_int = int(core[13:15])
        mn_int = int(core[16:18])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            59,
            999,
            999,
            999,
            unit,
        )

    elif real_len == 21:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[8:12])
        h_int = int(core[13:15])
        mn_int = int(core[16:18])
        sec_int = int(core[19:21])

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            999,
            999,
            999,
            unit,
        )

    elif real_len > 22:
        dy_int = int(core[0:2])
        month_abbrev = core[3:6]
        yr_int = int(core[8:12])
        h_int = int(core[13:15])
        mn_int = int(core[16:18])
        sec_int = int(core[19:21])

        # Position 21 is the fractional separator.
        fraction = core[22:real_len]

        try:
            mnth_int = ABREV_MONTH_ENG[month_abbrev]
        except KeyError:
            raise ValueError(
                f"Unsupported English month abbreviation: "
                f"{month_abbrev!r}"
            ) from None

        if not fraction.isdigit():
            raise ValueError(
                "Fractional seconds must contain only digits"
            )

        digits = len(fraction)

        if digits > 9:
            raise ValueError(
                "At most 9 fractional digits are supported"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

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
        raise ValueError(
            "Unsupported day-abbreviated-month comma datetime format"
        )

    return (
        lwr_bnd - tmz_offset_time,
        upr_bnd - tmz_offset_time,
    )

def detect_resolution2_compact_numeric(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if not s:
        raise ValueError("Empty datetime string")

    tmz = timezone_extractor(s)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1

        tmz_offset_time = (
            sign * get_time_tmz2(tmz[1:], unit)
        )
    else:
        # No timezone or Z.
        tmz_offset_time = 0

    if tmz:
        core = s[:-len(tmz)].rstrip()
    else:
        core = s

    real_len = len(core)

    # ---------------------------------------------------------
    # 2024
    # %Y
    # ---------------------------------------------------------
    if real_len == 4:
        yr_int = int(core[0:4])

        lwr_bnd = get_epoch(
            yr_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            12,
            31,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 202401
    # %Y%m
    # ---------------------------------------------------------
    elif real_len == 6:
        yr_int = int(core[0:4])
        mnth_int = int(core[4:6])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_max,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 20240131
    # %Y%m%d
    # ---------------------------------------------------------
    elif real_len == 8:
        yr_int = int(core[0:4])
        mnth_int = int(core[4:6])
        dy_int = int(core[6:8])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 2024013117
    # %Y%m%d%H
    # ---------------------------------------------------------
    elif real_len == 10:
        yr_int = int(core[0:4])
        mnth_int = int(core[4:6])
        dy_int = int(core[6:8])
        h_int = int(core[8:10])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 202401311712
    # %Y%m%d%H%M
    # ---------------------------------------------------------
    elif real_len == 12:
        yr_int = int(core[0:4])
        mnth_int = int(core[4:6])
        dy_int = int(core[6:8])
        h_int = int(core[8:10])
        mn_int = int(core[10:12])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 20240131171233
    # %Y%m%d%H%M%S
    # ---------------------------------------------------------
    elif real_len == 14:
        yr_int = int(core[0:4])
        mnth_int = int(core[4:6])
        dy_int = int(core[6:8])
        h_int = int(core[8:10])
        mn_int = int(core[10:12])
        sec_int = int(core[12:14])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 20240131171233.123...
    # %Y%m%d%H%M%S.%f
    # ---------------------------------------------------------
    elif real_len > 15:
        yr_int = int(core[0:4])
        mnth_int = int(core[4:6])
        dy_int = int(core[6:8])
        h_int = int(core[8:10])
        mn_int = int(core[10:12])
        sec_int = int(core[12:14])

        # Position 14 is the fractional separator.
        fraction = core[15:real_len]

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
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

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
        raise ValueError(
            "Unsupported compact numeric datetime format"
        )

    # Convert local wall-clock bounds to UTC.
    return (
        lwr_bnd - tmz_offset_time,
        upr_bnd - tmz_offset_time,
    )

def detect_resolution2_numeric_dmy(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if not s:
        raise ValueError("Empty datetime string")

    tmz = timezone_extractor(s)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1

        tmz_offset_time = (
            sign * get_time_tmz2(tmz[1:], unit)
        )
    else:
        # No timezone or Z.
        tmz_offset_time = 0

    if tmz:
        core = s[:-len(tmz)].rstrip()
    else:
        core = s

    real_len = len(core)

    if real_len == 7:
        mnth_int = int(core[0:2])
        yr_int = int(core[3:7])
    
        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )
    
        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )
    
        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            unit=unit,
        )
    
        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_max,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 31/01/2024
    # %d/%m/%Y
    # ---------------------------------------------------------
    elif real_len == 10:
        dy_int = int(core[0:2])
        mnth_int = int(core[3:5])
        yr_int = int(core[6:10])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 31/01/2024 17
    # %d/%m/%Y %H
    # ---------------------------------------------------------
    elif real_len == 13:
        dy_int = int(core[0:2])
        mnth_int = int(core[3:5])
        yr_int = int(core[6:10])
        h_int = int(core[11:13])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 31/01/2024 17:12
    # %d/%m/%Y %H:%M
    # ---------------------------------------------------------
    elif real_len == 16:
        dy_int = int(core[0:2])
        mnth_int = int(core[3:5])
        yr_int = int(core[6:10])
        h_int = int(core[11:13])
        mn_int = int(core[14:16])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 31/01/2024 17:12:33
    # %d/%m/%Y %H:%M:%S
    # ---------------------------------------------------------
    elif real_len == 19:
        dy_int = int(core[0:2])
        mnth_int = int(core[3:5])
        yr_int = int(core[6:10])
        h_int = int(core[11:13])
        mn_int = int(core[14:16])
        sec_int = int(core[17:19])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 31/01/2024 17:12:33.123...
    # %d/%m/%Y %H:%M:%S.%f
    # ---------------------------------------------------------
    elif real_len > 20:
        dy_int = int(core[0:2])
        mnth_int = int(core[3:5])
        yr_int = int(core[6:10])
        h_int = int(core[11:13])
        mn_int = int(core[14:16])
        sec_int = int(core[17:19])

        # Position 19 is the fractional separator.
        fraction = core[20:real_len]

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
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

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
        raise ValueError(
            "Unsupported numeric DMY datetime format"
        )

    # Convert the local wall-clock bounds into UTC.
    return (
        lwr_bnd - tmz_offset_time,
        upr_bnd - tmz_offset_time,
    )

def detect_resolution2_numeric_mdy(
    s: str,
    unit: str = "ns",
):
    s = s.strip()

    if not s:
        raise ValueError("Empty datetime string")

    tmz = timezone_extractor(s)

    if len(tmz) > 1:
        sign = -1 if tmz[0] == "-" else 1

        tmz_offset_time = (
            sign * get_time_tmz2(tmz[1:], unit)
        )
    else:
        tmz_offset_time = 0

    if tmz:
        core = s[:-len(tmz)].rstrip()
    else:
        core = s

    real_len = len(core)

    # ---------------------------------------------------------
    # 01/2024
    # %m/%Y
    # ---------------------------------------------------------
    if real_len == 7:
        mnth_int = int(core[0:2])
        yr_int = int(core[3:7])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_max,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 01/31/2024
    # %m/%d/%Y
    # ---------------------------------------------------------
    elif real_len == 10:
        mnth_int = int(core[0:2])
        dy_int = int(core[3:5])
        yr_int = int(core[6:10])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

        dy_max = (
            days_mnth_leap[mnth_int - 1]
            if is_leap(yr_int)
            else days_mnth[mnth_int - 1]
        )

        if not 1 <= dy_int <= dy_max:
            raise ValueError(
                f"Day must be between 1 and {dy_max}"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            23,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 01/31/2024 17
    # %m/%d/%Y %H
    # ---------------------------------------------------------
    elif real_len == 13:
        mnth_int = int(core[0:2])
        dy_int = int(core[3:5])
        yr_int = int(core[6:10])
        h_int = int(core[11:13])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            59,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 01/31/2024 17:12
    # %m/%d/%Y %H:%M
    # ---------------------------------------------------------
    elif real_len == 16:
        mnth_int = int(core[0:2])
        dy_int = int(core[3:5])
        yr_int = int(core[6:10])
        h_int = int(core[11:13])
        mn_int = int(core[14:16])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            59,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 01/31/2024 17:12:33
    # %m/%d/%Y %H:%M:%S
    # ---------------------------------------------------------
    elif real_len == 19:
        mnth_int = int(core[0:2])
        dy_int = int(core[3:5])
        yr_int = int(core[6:10])
        h_int = int(core[11:13])
        mn_int = int(core[14:16])
        sec_int = int(core[17:19])

        if not 1 <= mnth_int <= 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

        lwr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            unit=unit,
        )

        upr_bnd = get_epoch(
            yr_int,
            mnth_int,
            dy_int,
            h_int,
            mn_int,
            sec_int,
            999,
            999,
            999,
            unit,
        )

    # ---------------------------------------------------------
    # 01/31/2024 17:12:33.123...
    # %m/%d/%Y %H:%M:%S.%f
    # ---------------------------------------------------------
    elif real_len > 20:
        mnth_int = int(core[0:2])
        dy_int = int(core[3:5])
        yr_int = int(core[6:10])
        h_int = int(core[11:13])
        mn_int = int(core[14:16])
        sec_int = int(core[17:19])

        # Position 19 is the fractional separator.
        fraction = core[20:real_len]

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
            raise ValueError(
                "Month must be between 1 and 12"
            )

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
            raise ValueError(
                "Hour must be between 0 and 23"
            )

        if not 0 <= mn_int <= 59:
            raise ValueError(
                "Minute must be between 0 and 59"
            )

        if not 0 <= sec_int <= 59:
            raise ValueError(
                "Second must be between 0 and 59"
            )

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
        raise ValueError(
            "Unsupported numeric MDY datetime format"
        )

    return (
        lwr_bnd - tmz_offset_time,
        upr_bnd - tmz_offset_time,
    )

assert detect_resolution2_numeric_mdy(
    "01/2024",
    unit="ns",
) == (
    get_epoch(2024, 1, unit="ns"),
    get_epoch(
        2024, 1, 31,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

assert detect_resolution2_numeric_mdy(
    "01/31/2024",
    unit="ns",
) == (
    get_epoch(2024, 1, 31, unit="ns"),
    get_epoch(
        2024, 1, 31,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

assert detect_resolution2_month_day(
    "Jan 2024",
    unit="ns",
) == (
    get_epoch(2024, 1, 1, unit="ns"),
    get_epoch(
        2024, 1, 31,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

assert detect_resolution2_compact_numeric(
    "20240131",
    unit="ns",
) == (
    get_epoch(2024, 1, 31, unit="ns"),
    get_epoch(
        2024, 1, 31,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

assert detect_resolution2_numeric_dmy(
    "31-01-2024", 
    unit="ns",
) == (
    get_epoch(2024, 1, 31, unit="ns"),
    get_epoch(
        2024, 1, 31,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

# ------------------------------------------------------------
# Day resolution: "Jan 31 2024"
# ------------------------------------------------------------

assert detect_resolution2_month_day(
    "Jan 31 2024",
    unit="ns",
) == (
    get_epoch(2024, 1, 31, unit="ns"),
    get_epoch(
        2024, 1, 31,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)


# ------------------------------------------------------------
# Hour resolution
# ------------------------------------------------------------

assert detect_resolution2_month_day(
    "Jan 31 2024 17",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 31,
        17,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 31,
        17, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)


# ------------------------------------------------------------
# Minute resolution
# ------------------------------------------------------------

assert detect_resolution2_month_day(
    "Jan 31 2024 17:12",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 31,
        17, 12,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 31,
        17, 12, 59,
        999, 999, 999,
        unit="ns",
    ),
)


# ------------------------------------------------------------
# Second resolution
# ------------------------------------------------------------

assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 31,
        17, 12, 33,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 31,
        17, 12, 33,
        999, 999, 999,
        unit="ns",
    ),
)

second_base = get_epoch(
    2024, 1, 31,
    17, 12, 33,
    unit="ns",
)


# .1 means the interval:
# 100_000_000 ns through 199_999_999 ns
assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33.1",
    unit="ns",
) == (
    second_base + 100_000_000,
    second_base + 199_999_999,
)


# Millisecond precision
assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33.123",
    unit="ns",
) == (
    second_base + 123_000_000,
    second_base + 123_999_999,
)


# Microsecond precision
assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33.123456",
    unit="ns",
) == (
    second_base + 123_456_000,
    second_base + 123_456_999,
)


# Nanosecond precision: exact instant
assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33.123456789",
    unit="ns",
) == (
    second_base + 123_456_789,
    second_base + 123_456_789,
)

one_hour_ns = 60 * 60 * 1_000_000_000

local_second_base = get_epoch(
    2024, 1, 31,
    17, 12, 33,
    unit="ns",
)


# Z means already UTC.
assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33Z",
    unit="ns",
) == (
    local_second_base,
    local_second_base + 999_999_999,
)


# Local clock is one hour ahead of UTC:
# 17:12:33+01:00 -> 16:12:33Z
assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33+01:00",
    unit="ns",
) == (
    local_second_base - one_hour_ns,
    local_second_base - one_hour_ns + 999_999_999,
)


# Local clock is one hour behind UTC:
# 17:12:33-01:00 -> 18:12:33Z
assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33-01:00",
    unit="ns",
) == (
    local_second_base + one_hour_ns,
    local_second_base + one_hour_ns + 999_999_999,
)

assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33.123+01:00",
    unit="ns",
) == (
    local_second_base
    + 123_000_000
    - one_hour_ns,

    local_second_base
    + 123_999_999
    - one_hour_ns,
)

assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33.123 +01:00",
    unit="ns",
) == (
    local_second_base
    + 123_000_000
    - one_hour_ns,

    local_second_base
    + 123_999_999
    - one_hour_ns,
)

assert detect_resolution2_month_day(
    "Feb 2024",
    unit="ns",
) == (
    get_epoch(2024, 2, 1, unit="ns"),
    get_epoch(
        2024, 2, 29,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)


assert detect_resolution2_month_day(
    "Feb 2023",
    unit="ns",
) == (
    get_epoch(2023, 2, 1, unit="ns"),
    get_epoch(
        2023, 2, 28,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

second_base_us = get_epoch(
    2024, 1, 31,
    17, 12, 33,
    unit="us",
)

assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33.123",
    unit="us",
) == (
    second_base_us + 123_000,
    second_base_us + 123_999,
)


second_base_ms = get_epoch(
    2024, 1, 31,
    17, 12, 33,
    unit="ms",
)

assert detect_resolution2_month_day(
    "Jan 31 2024 17:12:33.1",
    unit="ms",
) == (
    second_base_ms + 100,
    second_base_ms + 199,
)

class ParsedDateTime:
    def __init__(self):
        self.year: int = 0
        self.month: int = 1
        self.day: int = 1

        self.hour: int = 0
        self.minute: int = 0
        self.second: int = 0

        self.fraction: int = 0
        self.fraction_digits: int = 0

        self.utc_offset: int = 0

        self.uses_12_hour_clock: bool = False
        self.am_pm: str = ""

        # year, month, day, hour, minute, second
        self.resolution = [0, 0, 0, 0, 0, 0]

# pass by reference
#def convertion_fn1(parsed: ParsedDateTime) -> ParsedDateTime:
#    return parsed

def get_int_len_pos(x: int) -> int:

    if x == 0:
        return 1

    cnt = 0

    while x > 0:
        x //= 10
        cnt += 1

    return cnt

def grab_fixed_digits(
    s: str,
    pos: int,
    width: int,
    field_name: str,
) -> tuple[str, int]:
    end = pos + width

    if end > len(s):
        raise ValueError(
            f"Not enough characters to parse {field_name}"
        )

    token = s[pos:end]

    if not token.isdigit():
        raise ValueError(
            f"{field_name} must contain exactly "
            f"{width} digits, got {token!r}"
        )

    return token, end

def grab_unit_year_2(
    s: str,
    pos: int,
) -> tuple[str, int]:
    return grab_fixed_digits(
        s,
        pos,
        2,
        "two-digit year",
    )


def conversion_year_2(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    year = int(token)

    if year <= 68:
        year += 2000
    else:
        year += 1900

    parsed.year = year
    parsed.resolution[0] = 1

    return parsed

def grab_unit_year_4(
    s: str,
    pos: int,
) -> tuple[str, int]:
    return grab_fixed_digits(
        s,
        pos,
        4,
        "year",
    )


def conversion_year_4(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    year = int(token)

    if year == 0:
        raise ValueError("Year 0 is not supported")

    parsed.year = year
    parsed.resolution[0] = 1

    return parsed

def grab_unit_month(
    s: str,
    pos: int,
) -> tuple[str, int]:
    return grab_fixed_digits(
        s,
        pos,
        2,
        "month",
    )


def conversion_month(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    month = int(token)

    if not 1 <= month <= 12:
        raise ValueError(
            "Month must be between 1 and 12"
        )

    parsed.month = month
    parsed.resolution[1] = 1

    return parsed

def grab_unit_day(
    s: str,
    pos: int,
) -> tuple[str, int]:
    return grab_fixed_digits(
        s,
        pos,
        2,
        "day",
    )


def conversion_day(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    day = int(token)

    if not 1 <= day <= 31:
        raise ValueError(
            "Day must be between 1 and 31"
        )

    parsed.day = day
    parsed.resolution[2] = 1

    return parsed

def grab_unit_hour_24(
    s: str,
    pos: int,
) -> tuple[str, int]:
    return grab_fixed_digits(
        s,
        pos,
        2,
        "hour",
    )


def conversion_hour_24(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    hour = int(token)

    if not 0 <= hour <= 23:
        raise ValueError(
            "Hour must be between 0 and 23"
        )

    parsed.hour = hour
    parsed.resolution[3] = 1

    return parsed

def grab_unit_hour_12(
    s: str,
    pos: int,
) -> tuple[str, int]:
    return grab_fixed_digits(
        s,
        pos,
        2,
        "12-hour clock hour",
    )


def conversion_hour_12(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    hour = int(token)

    if not 1 <= hour <= 12:
        raise ValueError(
            "12-hour clock hour must be between 1 and 12"
        )

    parsed.hour = hour
    parsed.uses_12_hour_clock = True
    parsed.resolution[3] = 1

    return parsed

def grab_unit_am_pm(
    s: str,
    pos: int,
) -> tuple[str, int]:
    end = pos + 2

    if end > len(s):
        raise ValueError(
            "Not enough characters to parse AM/PM"
        )

    token = s[pos:end]

    if token.upper() not in ("AM", "PM"):
        raise ValueError(
            f"Expected AM or PM, got {token!r}"
        )

    return token, end


def conversion_am_pm(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    parsed.am_pm = token.upper()
    return parsed

def apply_am_pm(
    parsed: ParsedDateTime,
) -> None:
    if not parsed.uses_12_hour_clock:
        if parsed.am_pm:
            raise ValueError(
                "%p requires the %I directive"
            )

        return

    if not parsed.am_pm:
        raise ValueError(
            "%I requires the %p directive"
        )

    if parsed.am_pm == "AM":
        if parsed.hour == 12:
            parsed.hour = 0
    else:
        if parsed.hour != 12:
            parsed.hour += 12

def grab_unit_minute(
    s: str,
    pos: int,
) -> tuple[str, int]:
    return grab_fixed_digits(
        s,
        pos,
        2,
        "minute",
    )


def conversion_minute(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    minute = int(token)

    if not 0 <= minute <= 59:
        raise ValueError(
            "Minute must be between 0 and 59"
        )

    parsed.minute = minute
    parsed.resolution[4] = 1

    return parsed

def grab_unit_second(
    s: str,
    pos: int,
) -> tuple[str, int]:
    return grab_fixed_digits(
        s,
        pos,
        2,
        "second",
    )

def conversion_second(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    second = int(token)

    if not 0 <= second <= 59:
        raise ValueError(
            "Second must be between 0 and 59"
        )

    parsed.second = second
    parsed.resolution[5] = 1

    return parsed

def grab_unit_fraction(
    s: str,
    pos: int,
    next_literal: str,
) -> tuple[str, int]:
    if next_literal:
        end = s.find(next_literal, pos)

        if end == -1:
            raise ValueError(
                f"Expected {next_literal!r} "
                "after fractional seconds"
            )
    else:
        end = len(s)

    token = s[pos:end]

    if not token:
        raise ValueError(
            "Fractional seconds cannot be empty"
        )

    if not token.isdigit():
        raise ValueError(
            "Fractional seconds must contain only digits"
        )

    if len(token) > 9:
        raise ValueError(
            "At most 9 fractional digits are supported"
        )

    return token, end

def conversion_fraction(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    parsed.fraction = int(token)
    parsed.fraction_digits = len(token)

    return parsed

def grab_unit_month_abbreviated(
    s: str,
    pos: int,
) -> tuple[str, int]:
    end = pos + 3

    if end > len(s):
        raise ValueError(
            "Not enough characters to parse "
            "an abbreviated month"
        )

    return s[pos:end], end

def conversion_month_abbreviated(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    normalized = token.capitalize()

    try:
        month = ABREV_MONTH_ENG[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Invalid abbreviated month: {token!r}"
        ) from exc

    parsed.month = month
    parsed.resolution[1] = 1

    return parsed

def grab_unit_month_full(
    s: str,
    pos: int,
    next_literal: str,
) -> tuple[str, int]:
    if next_literal:
        end = s.find(next_literal, pos)

        if end == -1:
            raise ValueError(
                f"Expected {next_literal!r} "
                "after the month name"
            )
    else:
        end = len(s)

    token = s[pos:end]

    if not token:
        raise ValueError(
            "Full month name cannot be empty"
        )

    return token, end

def conversion_month_full(
    parsed: ParsedDateTime,
    token: str,
) -> ParsedDateTime:
    normalized = token.capitalize()

    try:
        month = FULL_MONTH_ENG[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Invalid full month name: {token!r}"
        ) from exc

    parsed.month = month
    parsed.resolution[1] = 1

    return parsed

def grab_unit_timezone(
    s: str,
    pos: int,
    next_literal: str,
) -> tuple[str, int]:
    if pos >= len(s):
        raise ValueError("Missing timezone offset")

    if s[pos] == "Z":
        return "Z", pos + 1

    if s[pos] not in ("+", "-"):
        raise ValueError(
            "Timezone must start with '+', '-', or 'Z'"
        )

    if next_literal:
        end = s.find(next_literal, pos)

        if end == -1:
            raise ValueError(
                f"Expected {next_literal!r} after timezone"
            )
    else:
        end = len(s)

    token = s[pos:end]

    return token, end

def conversion_timezone(
    parsed: ParsedDateTime,
    token: str,
    unit: str,
) -> ParsedDateTime:
    if token == "Z":
        parsed.utc_offset = 0
        return parsed

    sign = -1 if token[0] == "-" else 1

    parsed.utc_offset = (
        sign * get_time_tmz2(token[1:], unit)
    )

    return parsed

DATE_KEYWORDS = {
    "%Y": (
        conversion_year_4,
        grab_unit_year_4,
        False,
    ),
    "%y": (
        conversion_year_2,
        grab_unit_year_2,
        False,
    ),
    "%m": (
        conversion_month,
        grab_unit_month,
        False,
    ),
    "%b": (
        conversion_month_abbreviated,
        grab_unit_month_abbreviated,
        False,
    ),
    "%B": (
        conversion_month_full,
        grab_unit_month_full,
        True,
    ),
    "%d": (
        conversion_day,
        grab_unit_day,
        False,
    ),
    "%H": (
        conversion_hour_24,
        grab_unit_hour_24,
        False,
    ),
    "%I": (
        conversion_hour_12,
        grab_unit_hour_12,
        False,
    ),
    "%M": (
        conversion_minute,
        grab_unit_minute,
        False,
    ),
    "%S": (
        conversion_second,
        grab_unit_second,
        False,
    ),
    "%f": (
        conversion_fraction,
        grab_unit_fraction,
        True,
    ),
    "%p": (
        conversion_am_pm,
        grab_unit_am_pm,
        False,
    ),
    "%z": (
        conversion_timezone,
        grab_unit_timezone,
        True,
    ),
}

NORMALIZE_MAX_DATE = {
    # Year resolution
    0: lambda x, isleap: (
        12,
        31,
        23,
        59,
        59,
    ),

    # Month resolution
    1: lambda x, isleap: (
        x[1],
        (
            days_mnth_leap[x[1] - 1]
            if isleap
            else days_mnth[x[1] - 1]
        ),
        23,
        59,
        59,
    ),

    # Day resolution
    2: lambda x, isleap: (
        x[1],
        x[2],
        23,
        59,
        59,
    ),

    # Hour resolution
    3: lambda x, isleap: (
        x[1],
        x[2],
        x[3],
        59,
        59,
    ),

    # Minute resolution
    4: lambda x, isleap: (
        x[1],
        x[2],
        x[3],
        x[4],
        59,
    ),

    # Second resolution
    5: lambda x, isleap: (
        x[1],
        x[2],
        x[3],
        x[4],
        x[5],
    ),
}

def validate_parsed_date(
    parsed: ParsedDateTime,
) -> None:
    if parsed.resolution[0] == 0:
        raise ValueError(
            "A year must be specified"
        )

    if parsed.resolution[1] == 0:
        return None

    if not 1 <= parsed.month <= 12:
        raise ValueError(
            "Month must be between 1 and 12"
        )

    if parsed.resolution[2] == 0:
        return None

    day_max = (
        days_mnth_leap[parsed.month - 1]
        if is_leap(parsed.year)
        else days_mnth[parsed.month - 1]
    )

    if not 1 <= parsed.day <= day_max:
        raise ValueError(
            f"Day must be between 1 and {day_max} "
            f"for year {parsed.year}, "
            f"month {parsed.month}"
        )

    return None

def detect_resolution2_general_date_parser(
    s: str,
    fmt: str,
    unit: str = "ns",
) -> tuple[int, int]:
    
    try:
        unit_digits = UNIT_DIGITS[unit]
    except KeyError as exc:
        raise ValueError(
            "unit must be 's', 'ms', 'us', or 'ns'"
        ) from exc

    parsed = ParsedDateTime()

    fmt_pos = 0
    s_pos = 0

    while fmt_pos < len(fmt):
        directive_pos = fmt.find("%", fmt_pos)

        # No more directives: match the remaining literal.
        if directive_pos == -1:
            literal = fmt[fmt_pos:]

            if not s.startswith(literal, s_pos):
                raise ValueError(
                    f"Expected literal {literal!r} "
                    f"at input position {s_pos}"
                )

            s_pos += len(literal)
            fmt_pos = len(fmt)
            break

        # Match text located before the next directive.
        literal = fmt[fmt_pos:directive_pos]

        if not s.startswith(literal, s_pos):
            raise ValueError(
                f"Expected literal {literal!r} "
                f"at input position {s_pos}"
            )

        s_pos += len(literal)

        if directive_pos + 1 >= len(fmt):
            raise ValueError(
                "Dangling '%' at the end of format"
            )

        directive = fmt[
            directive_pos:directive_pos + 2
        ]

        try:
            conversion_fn, grab_fn, needs_next_literal = (
                DATE_KEYWORDS[directive]
            )
        except KeyError as exc:
            raise ValueError(
                f"Unsupported datetime directive: "
                f"{directive!r}"
            ) from exc

        if needs_next_literal:

            next_fmt_pos = directive_pos + 2
            next_directive_pos = fmt.find("%", next_fmt_pos)

            if next_directive_pos == -1:
                next_literal = fmt[next_fmt_pos:]
            else:
                next_literal = fmt[
                    next_fmt_pos:next_directive_pos
                ]

            token, s_pos = grab_fn(
                s,
                s_pos,
                next_literal,
            )
        else:
            token, s_pos = grab_fn(
                s,
                s_pos,
            )

        if directive == "%z":
            parsed = conversion_fn(
                parsed,
                token,
                unit,
            )
        else:
            parsed = conversion_fn(
                parsed,
                token,
            )

        fmt_pos = directive_pos + 2

    if s_pos != len(s):
        raise ValueError(
            f"Unparsed input remains at position {s_pos}: "
            f"{s[s_pos:]!r}"
        )

    apply_am_pm(parsed)
    day_max = validate_parsed_date(parsed)

    if parsed.fraction_digits > 0:

        unit_digits = UNIT_DIGITS[unit]
        scale = POW10[unit_digits - parsed.fraction_digits]
        add_fraction = parsed.fraction * scale

        lwr_bnd = get_epoch(parsed.year,
                            parsed.month,
                            parsed.day,
                            parsed.hour,
                            parsed.minute,
                            parsed.second,
                            unit = unit) + add_fraction - parsed.utc_offset
        upr_bnd = lwr_bnd + scale - 1

    else:

        idx = 5 - parsed.resolution[::-1].index(1)

        lst_time_values = [parsed.year,
                           parsed.month,
                           parsed.day,
                           parsed.hour,
                           parsed.minute,
                           parsed.second]

        (
            max_month,
            max_day,
            max_hour,
            max_minute,
            max_second,
        ) = NORMALIZE_MAX_DATE[idx](
            lst_time_values,
            is_leap(parsed.year),
        )

        lwr_bnd = get_epoch(parsed.year,
                        parsed.month,
                        parsed.day,
                        parsed.hour,
                        parsed.minute,
                        parsed.second,
                        unit = unit) - parsed.utc_offset
        
        upr_bnd = get_epoch(parsed.year,
                            max_month,
                            max_day,
                            max_hour,
                            max_minute,
                            max_second,
                            999,
                            999,
                            999,
                            unit = unit) - parsed.utc_offset

    return (lwr_bnd, upr_bnd)


# ---------------------------------------------------------
# Year only
# 2024 -> entire year
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024",
    "%Y",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 1,
        0, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 12, 31,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Year + day, month omitted
# Month defaults to January.
#
# Mask: [1, 0, 1, 0, 0, 0]
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024-15",
    "%Y-%d",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        0, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Day before year in the format
# Parsing order must not affect the final resolution.
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "15/2024",
    "%d/%Y",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        0, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Year + hour
# Month and day default to January 1.
#
# Mask: [1, 0, 0, 1, 0, 0]
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024 17",
    "%Y %H",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 1,
        17, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 1,
        17, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Year + month + minute
# Day defaults to 1 and hour defaults to 0.
#
# Mask: [1, 1, 0, 0, 1, 0]
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024-02 34",
    "%Y-%m %M",
    unit="ns",
) == (
    get_epoch(
        2024, 2, 1,
        0, 34, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 2, 1,
        0, 34, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Year + second
# All intermediate components use their defaults.
#
# Mask: [1, 0, 0, 0, 0, 1]
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024 42",
    "%Y %S",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 1,
        0, 0, 42,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 1,
        0, 0, 42,
        999, 999, 999,
        unit="ns",
    ),
)

# February 2024 is a leap-year month with 29 days.
assert detect_resolution2_general_date_parser(
    "02/2024",
    "%m/%Y",
    unit="ns",
) == (
    get_epoch(
        2024, 2, 1,
        0, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 2, 29,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# February 2023 has 28 days.
assert detect_resolution2_general_date_parser(
    "02/2023",
    "%m/%Y",
    unit="ns",
) == (
    get_epoch(
        2023, 2, 1,
        0, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2023, 2, 28,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

second_base = get_epoch(
    2024, 1, 15,
    17, 12, 33,
    unit="ns",
)

assert detect_resolution2_general_date_parser(
    "2024-15 17:12:33.123",
    "%Y-%d %H:%M:%S.%f",
    unit="ns",
) == (
    second_base + 123_000_000,
    second_base + 123_999_999,
)

assert detect_resolution2_general_date_parser(
    "2024-15 17:12:33.000",
    "%Y-%d %H:%M:%S.%f",
    unit="ns",
) == (
    second_base,
    second_base + 999_999,
)

second_base_ms = get_epoch(
    2024, 1, 15,
    17, 12, 33,
    unit="ms",
)

assert detect_resolution2_general_date_parser(
    "2024-15 17:12:33.1",
    "%Y-%d %H:%M:%S.%f",
    unit="ms",
) == (
    second_base_ms + 100,
    second_base_ms + 199,
)

one_hour_ns = 3_600_000_000_000

local_second = get_epoch(
    2024, 1, 15,
    17, 12, 33,
    unit="ns",
)

assert detect_resolution2_general_date_parser(
    "2024-15 17:12:33+01:00",
    "%Y-%d %H:%M:%S%z",
    unit="ns",
) == (
    local_second - one_hour_ns,
    local_second - one_hour_ns + 999_999_999,
)

five_hours_ns = 5 * 3_600_000_000_000

assert detect_resolution2_general_date_parser(
    "2024-15 17:12:33-05:00",
    "%Y-%d %H:%M:%S%z",
    unit="ns",
) == (
    local_second + five_hours_ns,
    local_second + five_hours_ns + 999_999_999,
)

# ---------------------------------------------------------
# %I + %p: basic PM conversion
# 05 PM -> 17
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024-01-15 05 PM",
    "%Y-%m-%d %I %p",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        17, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        17, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# 12 AM -> 00
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024-01-15 12 AM",
    "%Y-%m-%d %I %p",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        0, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        0, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# 12 PM -> 12
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024-01-15 12 PM",
    "%Y-%m-%d %I %p",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        12, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        12, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# 01 AM -> 01
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024-01-15 01 AM",
    "%Y-%m-%d %I %p",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        1, 0, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        1, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Full 12-hour time
# 05:12:33 PM -> 17:12:33
# ---------------------------------------------------------
second_base = get_epoch(
    2024, 1, 15,
    17, 12, 33,
    unit="ns",
)

assert detect_resolution2_general_date_parser(
    "2024-01-15 05:12:33 PM",
    "%Y-%m-%d %I:%M:%S %p",
    unit="ns",
) == (
    second_base,
    second_base + 999_999_999,
)
# ---------------------------------------------------------
# Fractional second with PM
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "2024-01-15 05:12:33.123 PM",
    "%Y-%m-%d %I:%M:%S.%f %p",
    unit="ns",
) == (
    second_base + 123_000_000,
    second_base + 123_999_999,
)


# ---------------------------------------------------------
# Abbreviated month: Jan
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "15 Jan 2024",
    "%d %b %Y",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Abbreviated month: Feb in leap year
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "Feb 2024",
    "%b %Y",
    unit="ns",
) == (
    get_epoch(
        2024, 2, 1,
        unit="ns",
    ),
    get_epoch(
        2024, 2, 29,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Abbreviated month in MDY order
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "Jan 15, 2024",
    "%b %d, %Y",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Lowercase abbreviated month, provided your conversion
# normalizes with token.capitalize()
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "15 jan 2024",
    "%d %b %Y",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

# ---------------------------------------------------------
# Full month: January
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "15 January 2024",
    "%d %B %Y",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Variable-width full month: May
# This is important because May is only 3 characters.
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "15 May 2024",
    "%d %B %Y",
    unit="ns",
) == (
    get_epoch(
        2024, 5, 15,
        unit="ns",
    ),
    get_epoch(
        2024, 5, 15,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Variable-width full month: September
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "15 September 2024",
    "%d %B %Y",
    unit="ns",
) == (
    get_epoch(
        2024, 9, 15,
        unit="ns",
    ),
    get_epoch(
        2024, 9, 15,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Full month only with year
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "February 2023",
    "%B %Y",
    unit="ns",
) == (
    get_epoch(
        2023, 2, 1,
        unit="ns",
    ),
    get_epoch(
        2023, 2, 28,
        23, 59, 59,
        999, 999, 999,
        unit="ns",
    ),
)

# ---------------------------------------------------------
# Abbreviated month + PM
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "Jan 15, 2024 at 05:12:33 PM",
    "%b %d, %Y at %I:%M:%S %p",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        17, 12, 33,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        17, 12, 33,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Full month + PM
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "January 15, 2024 at 05:12:33 PM",
    "%B %d, %Y at %I:%M:%S %p",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        17, 12, 33,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        17, 12, 33,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Full month + 12 AM
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "January 15, 2024 at 12:30 AM",
    "%B %d, %Y at %I:%M %p",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        0, 30, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        0, 30, 59,
        999, 999, 999,
        unit="ns",
    ),
)
# ---------------------------------------------------------
# Full month + 12 PM
# ---------------------------------------------------------
assert detect_resolution2_general_date_parser(
    "January 15, 2024 at 12:30 PM",
    "%B %d, %Y at %I:%M %p",
    unit="ns",
) == (
    get_epoch(
        2024, 1, 15,
        12, 30, 0,
        unit="ns",
    ),
    get_epoch(
        2024, 1, 15,
        12, 30, 59,
        999, 999, 999,
        unit="ns",
    ),
)

one_hour_ns = 3_600_000_000_000

local_second = get_epoch(
    2024, 1, 15,
    17, 12, 33,
    unit="ns",
)

assert detect_resolution2_general_date_parser(
    "January 15, 2024 05:12:33 PM+01:00",
    "%B %d, %Y %I:%M:%S %p%z",
    unit="ns",
) == (
    local_second - one_hour_ns,
    local_second - one_hour_ns + 999_999_999,
)

base = get_epoch(
    2024, 1, 15,
    17, 12, 33,
    unit="ns",
)

assert detect_resolution2_general_date_parser(
    "Jan 15 2024 05:12:33.000 PM",
    "%b %d %Y %I:%M:%S.%f %p",
    unit="ns",
) == (
    base,
    base + 999_999,
)


