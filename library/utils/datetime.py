from datetime import datetime, timedelta, timezone, tzinfo
from typing import Optional

DATETIME_FORMATS = [
    "%Y:%m:%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
]


def parse_tz(tz_str: str) -> timezone:
    hours, minutes = tz_str.split(":")

    return timezone(timedelta(hours=int(hours), minutes=int(minutes)))


def strptime_multi(
    date_string: str,
    tz: tzinfo,
    default_format: Optional[str] = None,
    formats: list[str] = DATETIME_FORMATS,
) -> datetime:
    formats = (
        [default_format, *DATETIME_FORMATS]
        if default_format is not None
        else DATETIME_FORMATS
    )
    date: Optional[datetime] = None

    for format in formats:
        try:
            date = datetime.strptime(date_string, format)
        except ValueError:
            pass

    if date is None:
        raise ValueError(f"Could not parse date: {date_string}")

    if date.tzinfo is None:
        date = date.replace(tzinfo=tz)

    return date
