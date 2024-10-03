import logging

import numpy as np
import pandas as pd

REQUIRED_COLS = ["path", "content_hash", "lat", "long"]
SIMILARITY_THRESHOLD = 0.7


logger = logging.getLogger(__name__)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def _clean_metadata(metadata_df: pd.DataFrame) -> pd.DataFrame:
    metadata_df = metadata_df[metadata_df["content_hash"].notnull()].copy()

    required_columns = REQUIRED_COLS
    if "group" in metadata_df.columns:
        required_columns.append("group")

    metadata_df = metadata_df[required_columns]

    return metadata_df


def _compute_similarity(metadata_df_merged: pd.DataFrame) -> pd.Series:
    metadata_df_merged["distance"] = (
        (metadata_df_merged["lat_x"] - metadata_df_merged["lat_y"]).pow(2)
        + (metadata_df_merged["long_x"] - metadata_df_merged["long_y"]).pow(2)
    ).pow(0.5)
    metadata_df_merged = metadata_df_merged[
        metadata_df_merged["distance"] < 0.0001
    ].copy()

    metadata_df_merged["similarity"] = metadata_df_merged.apply(
        lambda row: cosine_similarity(row["content_hash_x"], row["content_hash_y"]),
        axis=1,
    )

    return metadata_df_merged["similarity"]


def _select_duplicates(metadata_df_merged: pd.DataFrame) -> pd.DataFrame:
    is_duplicate = metadata_df_merged["similarity"] > SIMILARITY_THRESHOLD

    if "group" in metadata_df_merged.columns:
        is_duplicate = is_duplicate & (
            metadata_df_merged["group_x"] == metadata_df_merged["group_y"]
        )

    return metadata_df_merged[is_duplicate][["path_x", "path_y"]]


def _get_root_images(duplicates: pd.DataFrame) -> pd.Series:
    root_images = duplicates[~duplicates["path_x"].isin(duplicates["path_y"])]
    root_images.index = pd.Index(root_images["path_x"])

    return root_images["path_x"]


def _get_indexed_duplicate(
    metadata_df: pd.DataFrame, duplicates: pd.DataFrame
) -> pd.Series:
    root_images = _get_root_images(duplicates)

    # Set index to path
    metadata_df["index"] = metadata_df.index
    metadata_df = metadata_df.set_index("path", drop=False)

    # Mark all duplicates
    metadata_df["has_duplicate"] = False
    metadata_df.loc[duplicates["path_x"], "has_duplicate"] = True
    metadata_df.loc[duplicates["path_y"], "has_duplicate"] = True

    # Set duplicate path for root images, and fill for duplicates
    metadata_df["duplicate_path"] = None
    metadata_df.loc[root_images, "duplicate_path"] = root_images
    metadata_df.loc[metadata_df["has_duplicate"], "duplicate_path"] = metadata_df[
        metadata_df["has_duplicate"]
    ]["duplicate_path"].ffill()

    # Remove duplicate path for root images
    metadata_df.loc[
        metadata_df["path"] == metadata_df["duplicate_path"], "duplicate_path"
    ] = None

    # Reset index to original index
    metadata_df = metadata_df.set_index("index")

    return metadata_df["duplicate_path"]


def detect_duplicate(metadata_df: pd.DataFrame) -> pd.Series:
    metadata_df = _clean_metadata(metadata_df)
    metadata_df_shifted = metadata_df.shift(-1)

    metadata_df_merged = pd.merge(
        left=metadata_df,
        right=metadata_df_shifted,
        left_index=True,
        right_index=True,
    ).dropna(subset=["path_x", "path_y"])

    metadata_df_merged["similarity"] = _compute_similarity(metadata_df_merged)
    metadata_df_merged = _select_duplicates(metadata_df_merged)

    return _get_indexed_duplicate(metadata_df, metadata_df_merged)
