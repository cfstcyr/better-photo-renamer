import logging
from pathlib import Path

import pandas as pd

from src.utils.input import confirm

logger = logging.getLogger(__name__)


def rename_files(
    paths: "pd.Series[Path]",  # type: ignore
    new_paths: "pd.Series[Path]",  # type: ignore
    *,
    ask_confirm: bool = True,
    dry_run: bool = False,
) -> None:
    temp: dict[Path, Path] = {}

    if dry_run:
        logger.info("Dry run enabled, no files will be renamed")

    for path, new_path in zip(paths, new_paths):
        if new_path.exists():
            temp_path = new_path.parent / f"{new_path.stem}_temp{new_path.suffix}"
            temp[new_path] = temp_path
            if not dry_run:
                new_path.rename(temp_path)
                logger.info(f"Renamed {new_path} to temp file {temp_path}")
            else:
                logger.info(f"Would rename {new_path} to temp file {temp_path}")

        if path in temp:
            path = temp.pop(path)
            logger.info(f"Using temp file {path} instead")

        if not ask_confirm or confirm(f"Rename {path} to {new_path}?"):
            if not dry_run:
                path.rename(new_path)
                logger.info(f"Renamed {path} to {new_path}")
            else:
                logger.info(f"Would rename {path} to {new_path}")

    if temp:
        raise RuntimeError(f"Temp files {temp.items()} were not used")
