from pathlib import Path
from .metadata_extractor import MetadataExtractor, MetadataExtractorConfig
from .metadata_extractor_image import MetadataExtractorImage
from .metadata_extractor_mov import MetadataExtractorMov
from src.utils.errors import FactoryError

METADATA_EXTRACTORS = [
    MetadataExtractorImage,
    MetadataExtractorMov,
]


def create_metadata_extractor(
    path: str | Path, config: MetadataExtractorConfig = MetadataExtractorConfig()
) -> MetadataExtractor:
    path = Path(path)

    for extractor in METADATA_EXTRACTORS:
        if path.suffix.lower() in extractor.allowed_extensions:
            return extractor(config)

    raise FactoryError(
        f"Cannot create MetadataExtractor: Unsupported file extension: {path.suffix}"
    )
