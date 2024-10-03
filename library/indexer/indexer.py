import numpy as np
import pandas as pd


def _set_index_metadata(metadata_df: pd.DataFrame, *, prefix: str = "") -> pd.DataFrame:
    # Save original index
    metadata_df[f"{prefix}index"] = metadata_df.index

    # Set global index
    metadata_df[f"{prefix}global_index"] = (
        pd.Series(range(len(metadata_df)), index=metadata_df.index) + 1
    )

    if "duplicate" in metadata_df.columns:
        root_images = metadata_df[metadata_df["duplicate"].isna()]["path"]
        duplicates = (
            metadata_df["duplicate"].dropna().drop_duplicates().reset_index(drop=True)
        )

        metadata_df[f"{prefix}original_index"] = np.nan
        metadata_df[f"{prefix}duplicate_index"] = None

        # Set index for original images
        metadata_df = metadata_df.set_index("path", drop=False)
        metadata_df.loc[root_images, f"{prefix}original_index"] = (
            pd.Series(range(len(root_images)), index=root_images) + 1
        )

        # Fill original index for duplicate images
        metadata_df[f"{prefix}original_index"] = (
            metadata_df[f"{prefix}original_index"].ffill().astype("int")
        )

        # Set duplicate index to 1 for the original image for each duplicate group
        metadata_df.loc[duplicates, f"{prefix}duplicate_index"] = 1

        # Set duplicate index to 2, 3, 4, ... for the duplicate images
        metadata_df = metadata_df.set_index("duplicate", drop=False)
        metadata_df.loc[duplicates, f"{prefix}duplicate_index"] = (
            metadata_df.loc[duplicates].groupby(level=0).cumcount() + 2
        )

    # Reset index to original index
    metadata_df = metadata_df.set_index(f"{prefix}index")

    return metadata_df


def index_metadata(metadata_df: pd.DataFrame) -> pd.DataFrame:
    metadata_df = _set_index_metadata(metadata_df)

    if "group" in metadata_df.columns:
        for group_index, group in metadata_df.groupby("group"):
            indexed_group = _set_index_metadata(group, prefix="group_")

            for col in indexed_group.columns:
                if col not in metadata_df.columns:
                    metadata_df[col] = None

            metadata_df.loc[indexed_group.index, indexed_group.columns] = indexed_group

    return metadata_df
