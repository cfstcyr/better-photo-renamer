import logging
from pathlib import Path

import pandas as pd

from library.file_operator.file_operator import FileOperator
from library.metadata_editor.metadata_editor import MetadataEditorConfig
from library.utils.input import confirm

logger = logging.getLogger(__name__)


def apply_changes(
    paths: "pd.Series[Path]",  # type: ignore
    new_paths: "pd.Series[Path]",  # type: ignore
    *,
    file_operator: FileOperator,
    metadata_editor_config: MetadataEditorConfig,
    ask_confirm: bool = True,
) -> None:
    temp: dict[Path, Path] = {}

    for path, new_path in zip(paths, new_paths):
        if new_path.exists():
            temp_path = new_path.parent / f"{new_path.stem}_temp{new_path.suffix}"
            temp[new_path] = temp_path
            file_operator(
                src=new_path,
                dest=temp_path,
                metadata_editor_config=metadata_editor_config,
                force=False,
            )

        if path in temp:
            path = temp.pop(path)
            logger.info(f"Using temp file {path} instead")

        if not ask_confirm or confirm(f"Rename {path} to {new_path}?"):
            file_operator(
                src=path,
                dest=new_path,
                metadata_editor_config=metadata_editor_config,
                force=False,
            )

    if temp:
        raise RuntimeError(f"Temp files {temp.items()} were not used")
