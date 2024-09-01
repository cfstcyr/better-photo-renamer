from typing import Optional
import uuid
import pandas as pd
from .tag_fn_wrapper import TagFn, tag_fn_wrapper


def tag_datetime(series: pd.Series, format: str = "%Y-%m-%d_%H-%M-%S") -> pd.Series:
    return series.dt.strftime(format)


def tag_number(series: pd.Series, pad: Optional[int] = None) -> pd.Series:
    res = series.astype("str")

    if pad is not None:
        res = res.str.pad(pad, "left", "0")

    return res


def tag_uuid(df: pd.DataFrame) -> pd.Series:
    return pd.Series([str(uuid.uuid4()) for _ in range(len(df))], index=df.index)


TAGS: dict[str, TagFn] = {
    "date": tag_fn_wrapper("creation_time", tag_datetime),
    "index": tag_fn_wrapper("index", tag_number),
    "filename": tag_fn_wrapper(
        lambda df: df["path"].map(lambda x: x.stem), lambda series: series
    ),
    "uuid": tag_uuid,
    "hash": tag_fn_wrapper("metadata_hash", lambda series: series),
}
