import logging

import pandas as pd

from .distance_calculator import DistanceCalculator2, DistanceCalculatorN

logger = logging.getLogger(__name__)


def match_medias_all(
    distance_calculators: dict[str, DistanceCalculator2 | DistanceCalculatorN],
    result_distance_calculator: DistanceCalculatorN,
    medias: pd.DataFrame,
    medias_match: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if medias_match is None:
        medias_match = medias.copy()

    medias_df = medias.reset_index()
    medias_match_df = medias_match.reset_index().add_suffix("_match", axis=1)

    medias_df["pivot"] = 0
    medias_match_df["pivot"] = 0

    merged_df = pd.merge(
        left=medias_df,
        right=medias_match_df,
        on="pivot",
    )
    merged_df = merged_df.drop(columns=["pivot"])
    merged_df = merged_df[
        merged_df[medias.index.name]
        != merged_df[str(medias_match.index.name) + "_match"]
    ]

    distance_columns = []
    for dist_col, dist_calc in distance_calculators.items():
        logger.info(f"Calculating distance for {dist_col} with {dist_calc.__name__}")  # type: ignore
        dist_col_res = dist_col + "_distance"
        distance_columns.append(dist_col_res)

        merged_df[dist_col_res] = dist_calc(
            merged_df[dist_col], merged_df[dist_col + "_match"]
        )

    if len(distance_columns) == 1:
        merged_df["distance"] = merged_df[distance_columns[0]]
    else:
        merged_df["distance"] = result_distance_calculator(
            *(merged_df[dist_col] for dist_col in distance_columns)
        )

    merged_df = (
        merged_df.sort_values("distance", ascending=True)
        .drop_duplicates(subset=[medias.index.name])
        .set_index(medias.index.name)
        .rename(columns={str(medias_match.index.name) + "_match": "match"})
        .sort_index()
    )

    return merged_df[["match", "distance"]]


def match_medias(
    distance_calculator: DistanceCalculator2,
    medias: pd.Series,
    medias_match: pd.Series | None = None,
) -> pd.DataFrame:
    if medias_match is None:
        medias_match = medias.copy()

    medias_df = pd.DataFrame(medias, index=medias.index).reset_index()
    medias_match_df = (
        pd.DataFrame(medias_match, index=medias_match.index)
        .reset_index()
        .add_suffix("_match", axis=1)
    )

    medias_df["pivot"] = 0
    medias_match_df["pivot"] = 0

    merged_df = pd.merge(
        left=medias_df,
        right=medias_match_df,
        on="pivot",
    )
    merged_df = merged_df.drop(columns=["pivot"])
    merged_df = merged_df[
        merged_df[medias.index.name]
        != merged_df[str(medias_match.index.name) + "_match"]
    ]

    merged_df["distance"] = distance_calculator(
        merged_df[medias.name], merged_df[str(medias_match.name) + "_match"]
    )

    merged_df = (
        merged_df.sort_values("distance", ascending=False)
        .drop_duplicates(subset=[medias.index.name])
        .set_index(medias.index.name)
        .rename(columns={str(medias_match.index.name) + "_match": "match"})
        .sort_index()
    )

    return merged_df[["match", "distance"]]
