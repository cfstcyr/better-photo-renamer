import pandas as pd

from library.utils.df import split_match


def split_live_photos(metadata_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the metadata DataFrame into two DataFrames: one for live photos and one for still photos.

    Args:
        metadata_df: Metadata DataFrame.

    Returns:
        Tuple of two DataFrames: one for live photos and one for still photos.
    """
    metadata_df, metadata_live_df = split_match(
        metadata_df, split_col="is_live_photo", match_col="creation_time"
    )

    return metadata_df, metadata_live_df


def merge_live_photos(
    metadata_live_df: pd.DataFrame, metadata_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge the live photos DataFrame with the new path Series.

    Args:
        metadata_live_df: Live photos DataFrame.
        metadata_df: Metadata DataFrame.

    Returns:
        DataFrame with both live and still photos with the new path Series.
    """
    metadata_live_df = pd.merge(
        left=metadata_live_df,
        right=metadata_df["new_path"],
        left_on="match_index",
        right_index=True,
    )
    metadata_live_df["new_path"] = metadata_live_df.apply(
        lambda row: row["path"].parent
        / f"{row['new_path'].stem}_live{row['path'].suffix}",
        axis=1,
    )

    return pd.concat(
        [metadata_df[["path", "new_path"]], metadata_live_df[["path", "new_path"]]]
    )
