import logging
from typing import Callable, Literal

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from tqdm import tqdm

logger = logging.getLogger(__name__)


def _group_exact(metadata_df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    metadata_df["group"] = -1

    for i, (_, metadata_group) in enumerate(metadata_df.groupby(group_cols)):
        metadata_df.loc[metadata_group.index, "group"] = i

    return metadata_df


def _group_k_means_auto(
    metadata_df: pd.DataFrame, group_cols: list[str], *, k_max: int
) -> pd.DataFrame:
    score, best_k, result = -1, -1, None
    lower_score_count = 0

    for k in tqdm(range(2, k_max + 1)):
        k_means = KMeans(n_clusters=k, random_state=0)
        labels = k_means.fit_predict(metadata_df[group_cols])
        new_score = silhouette_score(metadata_df[group_cols], labels)

        if new_score > score:
            score = new_score
            best_k = k
            result = labels
            lower_score_count = 0
        else:
            lower_score_count += 1

            # Stop if the score is decreasing, but only after a few iterations (trying to ignore local minima)
            if lower_score_count > 5:
                break

    logger.info(f"Grouped into optimal {best_k} groups")

    metadata_df["group"] = result

    return metadata_df


def _group_k_means_n(
    metadata_df: pd.DataFrame, group_cols: list[str], n: int
) -> pd.DataFrame:
    k_means = KMeans(n_clusters=n, random_state=0)
    metadata_df["group"] = k_means.fit_predict(metadata_df[group_cols])

    return metadata_df


def _group_k_means(
    metadata_df: pd.DataFrame,
    group_cols: list[str],
    *,
    n: int | Literal["auto"] = "auto",
) -> pd.DataFrame:
    if n == "auto":
        return _group_k_means_auto(metadata_df, group_cols, k_max=len(metadata_df) // 2)
    elif isinstance(n, int):
        return _group_k_means_n(metadata_df, group_cols, n)

    raise ValueError(f"Invalid value for n: {n}. Must be an integer or 'auto'.")


GROUPING_METHODS: dict[str, Callable[[pd.DataFrame, list[str]], pd.DataFrame]] = {
    "exact": _group_exact,
    "k_means": _group_k_means,
}
