from typing import Callable

import pandas as pd
from sklearn.cluster import KMeans


def _group_exact(metadata_df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    metadata_df["group"] = -1

    for i, (_, metadata_group) in enumerate(metadata_df.groupby(group_cols)):
        metadata_df.loc[metadata_group.index, "group"] = i

    return metadata_df


def _group_k_means(
    metadata_df: pd.DataFrame, group_cols: list[str], *, n: int = 3
) -> pd.DataFrame:
    k_means = KMeans(n_clusters=n, random_state=0)
    metadata_df["group"] = k_means.fit_predict(metadata_df[group_cols])

    return metadata_df


GROUPING_METHODS: dict[str, Callable[[pd.DataFrame, list[str]], pd.DataFrame]] = {
    "exact": _group_exact,
    "k_means": _group_k_means,
}
