import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from library.cache import Cache
from library.metadata_extractor import Metadata
from library.utils.df import explode_dict

from .metadata_extractor import MetadataExtractorConfig, create_metadata_extractor

logger = logging.getLogger(__name__)


def _load_metadata_from_path(
    path: Path, metadata_config: MetadataExtractorConfig, cache: Cache | None = None
) -> Metadata:
    path_str = str(path)
    if cache is not None and cache.has(path_str):
        logger.debug(f"Load metadata from cache: {path}")
        cache_hit = cache.get(path_str)

        if cache_hit is not None:
            return cache_hit

        logger.warning(f"Cache hit is None: {path}")

    metadata = create_metadata_extractor(path, config=metadata_config).extract(path)

    if cache is not None:
        cache.set(path_str, metadata)

    return metadata


def load_metadata(
    paths: list[Path],
    metadata_config: MetadataExtractorConfig,
    cache: Cache | None = None,
) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "path": paths,
            "metadata": tqdm(
                (
                    _load_metadata_from_path(path, metadata_config, cache=cache)
                    for path in paths
                ),
                total=len(paths),
                desc="Extracting metadata",
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
