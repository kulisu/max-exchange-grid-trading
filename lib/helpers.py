#!/usr/bin/env python3

from datetime import datetime as _datetime, date as _date, timedelta
from hashlib import md5
from time import time as _time


def convert_to_date(timestamp, pattern='%Y/%m/%d'):
    return _datetime.fromtimestamp(int(timestamp / 1000 if len(str(timestamp)) == 13 else 1)).strftime(pattern)


def convert_to_time(timestamp, pattern='%H:%M:%S'):
    parsed = _datetime.fromtimestamp(int(timestamp / 1000 if len(str(timestamp)) == 13 else 1)).strftime(pattern)

    if '%f' in pattern:
        return f"{parsed.split('.')[0]}.{str(timestamp)[-3:]}"

    return parsed


def get_current_timestamp():
    return int(round(_time() * 1000))


def get_md5_checksum(value, full=False):
    checksum = md5(value.encode('utf-8')).hexdigest()

    return checksum if full else checksum[8:-8]


def get_shifted_day(shift, pattern='%Y%m%d'):
    return (_date.today() - timedelta(shift)).strftime(pattern)


def get_truncated_value(value, decimal=8):
    _int, _float = f"{float(value):.8f}".split('.')
    truncated = f"{int(_int)}.{_float[0:decimal]}"

    return float(f"{float(truncated):.{decimal}f}") if decimal > 0 else int(f"{float(truncated):.{decimal}f}")


def get_readable_timestamp():
    return _datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f')