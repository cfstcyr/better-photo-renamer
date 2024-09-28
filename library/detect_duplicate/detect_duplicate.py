import numpy as np
import pandas as pd

SIMILARITY_THRESHOLD = 0.7


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def detect_duplicate(metadata_df: pd.DataFrame) -> pd.Series:
    metadata_df = metadata_df[metadata_df["content_hash"].notnull()].copy()
    metadata_df_shifted = metadata_df.shift(-1)

    metadata_df_merged = pd.merge(
        left=metadata_df,
        right=metadata_df_shifted,
        left_index=True,
        right_index=True,
    ).dropna()

    metadata_df_merged["distance"] = (
        (metadata_df_merged["lat_x"] - metadata_df_merged["lat_y"]).pow(2)
        + (metadata_df_merged["long_x"] - metadata_df_merged["long_y"]).pow(2)
    ).pow(0.5)
    metadata_df_merged = metadata_df_merged[metadata_df_merged["distance"] < 0.0001]

    metadata_df_merged["similarity"] = metadata_df_merged.apply(
        lambda row: cosine_similarity(row["content_hash_x"], row["content_hash_y"]),
        axis=1,
    )
    metadata_df_merged = metadata_df_merged[
        metadata_df_merged["similarity"] > SIMILARITY_THRESHOLD
    ]

    metadata_df_end = metadata_df_merged[
        [col for col in metadata_df_merged.columns if col.endswith("_y")]
    ].copy()
    metadata_df_end.columns = [col.replace("_y", "") for col in metadata_df_end.columns]

    metadata_df_merged_deep = pd.merge(
        left=metadata_df_merged,
        right=metadata_df_end.shift(1),
        left_index=True,
        right_index=True,
    )
    is_root_image = (
        metadata_df_merged_deep["path_x"] != metadata_df_merged_deep["path"]
    ) | metadata_df_merged_deep["path"].isnull()
    metadata_df_merged_deep.loc[is_root_image, "duplicated_path"] = (
        metadata_df_merged_deep["path_x"]
    )
    metadata_df_merged_deep["duplicated_path"] = metadata_df_merged_deep[
        "duplicated_path"
    ].ffill()

    metadata_df = pd.merge(
        left=metadata_df,
        right=metadata_df_merged_deep[["path_y", "duplicated_path"]].rename(
            columns={"path_y": "path"}
        ),
        on="path",
        how="left",
    )

    return metadata_df["duplicated_path"]
