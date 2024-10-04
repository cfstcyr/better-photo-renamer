import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, tzinfo
from pathlib import Path

from pytz import timezone

from library.utils.datetime import strptime_multi
from library.utils.dict import get_dict_value
from library.utils.errors import ExtractionError

from .metadata import Metadata

logger = logging.getLogger(__name__)


@dataclass
class MetadataEditorConfig:
    tz: tzinfo = timezone("Europe/Paris")
    extract_content_hash: bool = False


class MetadataEditor(ABC):
    config: MetadataEditorConfig
    _allowed_extensions: list[str]
    _creation_time_keys: list[str]

    def __init__(self, config: MetadataEditorConfig) -> None:
        self.config = config

    def extract(self, path: Path | str) -> Metadata:
        try:
            return self._extract(Path(path))
        except ExtractionError as e:
            raise ExtractionError(f"Error extracting metadata from {path}: {e}")

    @classmethod
    def can_edit(cls, path: Path) -> bool:
        return path.suffix.lower() in cls._allowed_extensions

    @abstractmethod
    def _extract(self, path: Path) -> Metadata: ...

    def _extract_creation_time(self, path: Path, tags: dict) -> datetime:
        for key in self._creation_time_keys:
            value = get_dict_value(tags, key)
            if value is not None:
                return strptime_multi(
                    date_string=value,
                    tz=self.config.tz,
                    default_format="%Y-%m-%dT%H:%M:%S.%fZ",
                )

        creation_time = datetime.fromtimestamp(path.stat().st_ctime, tz=self.config.tz)
        logger.warning(
            f"Could not find creation time in {path}. "
            f"Using file creation time {creation_time}. "
        )

        return creation_time
