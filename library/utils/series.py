from typing import Literal

import pandas as pd

Pad = int | Literal["auto"]


def pad_series(series: pd.Series, pad: Pad, fill: str = "0") -> pd.Series:
    if pad == "auto":
        pad = series.astype("str").str.len().max()

    series = series.astype("str").str.pad(pad, "left", fill)

    return series
