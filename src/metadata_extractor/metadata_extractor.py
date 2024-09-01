from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import tzinfo
from pathlib import Path

from pytz import timezone

from src.utils.errors import ExtractionError

from .metadata import Metadata


@dataclass
class MetadataExtractorConfig:
    tz: tzinfo = timezone("Europe/Paris")


class MetadataExtractor(ABC):
    config: MetadataExtractorConfig
    allowed_extensions: list[str]

    def __init__(self, config: MetadataExtractorConfig) -> None:
        self.config = config

    def extract(self, path: Path | str) -> Metadata:
        try:
            return self._extract(Path(path))
        except ExtractionError as e:
            raise ExtractionError(f"Error extracting metadata from {path}: {e}")

    @abstractmethod
    def _extract(self, path: Path) -> Metadata: ...
