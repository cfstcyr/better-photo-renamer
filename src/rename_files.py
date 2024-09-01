import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def rename_files(
    paths: "pd.Series[Path]",  # type: ignore
    new_paths: "pd.Series[Path]",  # type: ignore
) -> None:
    temp: dict[Path, Path] = {}

    for path, new_path in zip(paths, new_paths):
        if new_path.exists():
            temp_path = new_path.parent / f"{new_path.stem}_temp{new_path.suffix}"
            temp[new_path] = temp_path
            new_path.rename(temp_path)
            logger.info(f"Renamed {new_path} to temp file {temp_path}")

        if path in temp:
            path = temp.pop(path)
            logger.info(f"Using temp file {path} instead")

        path.rename(new_path)
        logger.info(f"Renamed {path} to {new_path}")

    if temp:
        raise RuntimeError(f"Temp files {temp.items()} were not used")
