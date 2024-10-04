from pathlib import Path

from library.utils.errors import FactoryError

from .metadata_editor import MetadataEditor, MetadataEditorConfig
from .metadata_editor_image import MetadataEditorImage
from .metadata_editor_mov import MetadataEditorMov

METADATA_EDITORS: list[type[MetadataEditor]] = [
    MetadataEditorImage,
    MetadataEditorMov,
]


def create_metadata_editor(
    path: str | Path, config: MetadataEditorConfig = MetadataEditorConfig()
) -> MetadataEditor:
    path = Path(path)

    for editor in METADATA_EDITORS:
        if editor.can_edit(path):
            return editor(config)

    raise FactoryError(
        f"Cannot create {MetadataEditor.__name__}: Unsupported file extension: {path.suffix}"
    )
