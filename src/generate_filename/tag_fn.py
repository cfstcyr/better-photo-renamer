import uuid
from typing import Optional

import pandas as pd

from .tag_fn_wrapper import TagFn, tag_fn_wrapper


def tag_datetime(series: pd.Series, format: str = "%Y-%m-%d_%H-%M-%S") -> pd.Series:
    return series.dt.strftime(format)


def tag_number(
    series: pd.Series, *, round: Optional[int] = None, pad: Optional[int] = None
) -> pd.Series:
    res = series

    if round is not None:
        res = res.round(round)

    if pad is not None:
        res = res.astype("str").str.pad(pad, "left", "0")

    return res


def tag_index(
    series: pd.Series, pad: Optional[int] = None, start: int = 0
) -> pd.Series:
    return tag_number(series=series + start, pad=pad)


def tag_uuid(df: pd.DataFrame) -> pd.Series:
    return pd.Series([str(uuid.uuid4()) for _ in range(len(df))], index=df.index)


TAGS: dict[str, TagFn] = {
    "date": tag_fn_wrapper("creation_time", tag_datetime),
    "index": tag_fn_wrapper("index", tag_index),
    "filename": tag_fn_wrapper(
        lambda df: df["path"].map(lambda x: x.stem), lambda series: series
    ),
    "uuid": tag_uuid,
    "hash": tag_fn_wrapper("metadata_hash", lambda series: series),
    "lat": tag_fn_wrapper("gps_latitude", tag_number),
    "long": tag_fn_wrapper("gps_longitude", tag_number),
}
