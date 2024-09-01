from datetime import datetime, tzinfo
from typing import Optional

DATETIME_FORMATS = [
    "%Y:%m:%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
]


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
        date = date.astimezone(tz)

    return date
