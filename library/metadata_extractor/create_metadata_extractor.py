from pathlib import Path

from library.utils.errors import FactoryError

from .metadata_extractor import MetadataExtractor, MetadataExtractorConfig
from .metadata_extractor_image import MetadataExtractorImage
from .metadata_extractor_mov import MetadataExtractorMov

METADATA_EXTRACTORS: list[type[MetadataExtractor]] = [
    MetadataExtractorImage,
    MetadataExtractorMov,
]


def create_metadata_extractor(
    path: str | Path, config: MetadataExtractorConfig = MetadataExtractorConfig()
) -> MetadataExtractor:
    path = Path(path)

    for extractor in METADATA_EXTRACTORS:
        if extractor.can_extract(path):
            return extractor(config)

    raise FactoryError(
        f"Cannot create MetadataExtractor: Unsupported file extension: {path.suffix}"
    )
