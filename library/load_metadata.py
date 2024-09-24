from pathlib import Path

import pandas as pd

from library.utils.df import explode_dict

from .metadata_extractor import MetadataExtractorConfig, create_metadata_extractor


def load_metadata(
    paths: list[Path], metadata_config: MetadataExtractorConfig
) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "path": paths,
            "metadata": map(
                lambda x: create_metadata_extractor(x, config=metadata_config).extract(
                    x
                ),
                paths,
            ),
        }
    )
    df["ext"] = df["path"].map(lambda x: x.suffix)

    metadata_df = explode_dict(df, col="metadata")
    metadata_df["creation_time"] = pd.to_datetime(
        metadata_df["creation_time"], utc=True
    )

    df.loc[:, metadata_df.columns] = metadata_df
    df = df.drop(columns=["metadata"])
    df = df.sort_values(by=["creation_time", "metadata_hash"]).reset_index(drop=True)

    return df
