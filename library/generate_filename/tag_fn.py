import uuid
from typing import Optional

import pandas as pd

from library.utils.series import Pad, pad_series

from .tag_fn_wrapper import TagFn, tag_fn_wrapper


def tag_datetime(series: pd.Series, format: str = "%Y-%m-%d_%H-%M-%S") -> pd.Series:
    return series.dt.strftime(format)


def tag_number(
    series: pd.Series,
    *,
    round: Optional[int] = None,
    pad: Optional[Pad] = None,
    pad_fill: str = "0",
) -> pd.Series:
    res = series

    if round is not None:
        res = res.round(round)

    if pad is not None:
        res = pad_series(res, pad, pad_fill)

    return res


def tag_uuid(df: pd.DataFrame) -> pd.Series:
    return pd.Series([str(uuid.uuid4()) for _ in range(len(df))], index=df.index)


def tag_index_str(prefix: str = "") -> TagFn:
    def tag_index_str_fn(df: pd.DataFrame, *, sep: str = "-") -> pd.Series:
        res = pad_series(df[f"{prefix}original_index"].astype("str"), pad="auto")
        res.loc[df["duplicate_index"].notnull()] += sep + pad_series(
            df.loc[df[f"{prefix}duplicate_index"].notnull()]["duplicate_index"].astype(
                "str"
            ),
            pad="auto",
        )

        return res

    return tag_index_str_fn


def tag_if_exists(
    df: pd.DataFrame,
    column_or_series: str | pd.Series,
    if_exists: str | pd.Series,
    if_not_exists: str | pd.Series | None = None,
) -> pd.Series:
    predicate = (
        column_or_series
        if isinstance(column_or_series, pd.Series)
        else df[column_or_series]
    ).notnull()
    if_not_exists = if_not_exists if if_not_exists is not None else ""

    result = pd.Series("" * len(df), index=df.index)

    result[predicate] = if_exists
    result[~predicate] = if_not_exists

    return result


def tag_concat(df: pd.DataFrame, *args: pd.Series | str) -> pd.Series:
    result = pd.Series("", index=df.index)

    for arg in args:
        if isinstance(arg, pd.Series):
            result += arg.astype("str")
        else:
            result += arg

    return result


TAGS: dict[str, TagFn] = {
    "date": tag_fn_wrapper("creation_time", tag_datetime),
    "index": tag_fn_wrapper("global_index", tag_number),
    "index_str": tag_index_str(),
    "original_index": tag_fn_wrapper("original_index", tag_number),
    "duplicate_index": tag_fn_wrapper("duplicate_index", tag_number),
    "group_index": tag_fn_wrapper("group_global_index", tag_number),
    "group_index_str": tag_index_str("group_"),
    "group_original_index": tag_fn_wrapper("group_original_index", tag_number),
    "group_duplicate_index": tag_fn_wrapper("group_duplicate_index", tag_number),
    "filename": tag_fn_wrapper(
        lambda df: df["path"].map(lambda x: x.stem), lambda series: series
    ),
    "duplicate_name": tag_fn_wrapper(
        lambda df: df["duplicate"].map(
            lambda x: pd.NA if isinstance(x, float) else x.stem
        )
        if "duplicate" in df
        else pd.Series([pd.NA] * len(df)),
        lambda series: series,
    ),
    "uuid": tag_uuid,
    "hash": tag_fn_wrapper("metadata_hash", lambda series: series),
    "lat": tag_fn_wrapper("lat", tag_number),
    "long": tag_fn_wrapper("long", tag_number),
    "group": tag_fn_wrapper("group", tag_number),
    "if_exists": tag_if_exists,
    "concat": tag_concat,
}
