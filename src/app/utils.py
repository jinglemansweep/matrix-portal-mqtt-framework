import gc
import json
import math
import time
import adafruit_requests as requests

from app.constants import DEBUG


def logger(msg, *args):
    _log_print("INFO", msg, *args)


def debug(msg, *args):
    global DEBUG
    if DEBUG:
        _log_print("DEBUG", msg, *args)


def _log_print(level, msg, *args):
    print(f"{level} [mem:{gc.mem_free()}] > {msg}", *args)


def matrix_rotation(accelerometer):
    return (
        int(
            (
                (
                    math.atan2(
                        -accelerometer.acceleration.y, -accelerometer.acceleration.x
                    )
                    + math.pi
                )
                / (math.pi * 2)
                + 0.875
            )
            * 4
        )
        % 4
    ) * 90


def fetch_json(url, retry_count=3):
    failures = 0
    response = None
    logger(f"json fetch: url={url} retry_count={retry_count}")
    while not response:
        try:
            response = requests.get(url)
            failures = 0
        except AssertionError as error:
            logger(f"fetch retrying: error={error}")
            failures += 1
            if failures >= retry_count:
                raise AssertionError("fetch error") from error
            continue
    return json.loads(response.text)


def parse_timestamp(timestamp, is_dst=-1):
    # 2022-11-04 21:46:57.174 308 5 +0000 UTC
    bits = timestamp.split("T")
    year_month_day = bits[0].split("-")
    hour_minute_second = bits[1].split(":")
    return time.struct_time(
        (
            int(year_month_day[0]),
            int(year_month_day[1]),
            int(year_month_day[2]),
            int(hour_minute_second[0]),
            int(hour_minute_second[1]),
            int(hour_minute_second[2].split(".")[0]),
            -1,
            -1,
            is_dst,
        )
    )


def rgb2hex(r, g, b):
    return (r << 16) + (g << 8) + b
