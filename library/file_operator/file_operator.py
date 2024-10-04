import logging
from pathlib import Path
from typing import Protocol

from library.metadata_editor.metadata_editor import MetadataEditorConfig
from library.utils.input import confirm

logger = logging.getLogger(__name__)


def _check_overwrite(dest: Path, *, force: bool = False) -> None:
    if dest.exists():
        if force:
            logger.debug(f"Overwriting {dest}")
            dest.unlink()
        elif confirm(f"File {dest} already exists, overwrite?"):
            dest.unlink()
        else:
            raise FileExistsError(f"File {dest} already exists")


class FileOperator(Protocol):
    def __call__(
        self, src: str | Path, dest: str | Path, *, metadata_editor_config: MetadataEditorConfig, force: bool = False
    ) -> None: ...


def rename_file(src: str | Path, dest: str | Path, *, metadata_editor_config: MetadataEditorConfig, force: bool = False) -> None:
    src = Path(src)
    dest = Path(dest)

    _check_overwrite(dest, force=force)

    dest.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dest)

    logger.info(f"Renamed {src} to {dest}")


# def move_file(src: str | Path, dest: str | Path, *, metadata_editor_config: MetadataEditorConfig, force: bool = False) -> None:
#     src = Path(src)
#     dest = Path(dest)

#     _check_overwrite(dest, force=force)

#     src.replace(dest)

#     logger.debug(f"Moved {src} to {dest}")


def dry_run_file(src: str | Path, dest: str | Path, *, metadata_editor_config: MetadataEditorConfig, force: bool = False) -> None:
    src = Path(src)
    dest = Path(dest)

    _check_overwrite(dest, force=force)

    logger.info(f"Would rename \n\t{src} to \n\t{dest}")


FILE_OPERATORS: dict[str, FileOperator] = {
    "rename": rename_file,
    # "move": move_file,
    "dry-run": dry_run_file,
}
