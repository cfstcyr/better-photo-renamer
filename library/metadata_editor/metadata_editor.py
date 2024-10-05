import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, tzinfo
from pathlib import Path

from pytz import timezone

from library.utils.datetime import parse_tz, strptime_multi
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

    def _extract_creation_time(
        self, path: Path, datetime_str: str | None, tz_str: str | None = None
    ) -> datetime:
        if datetime_str is not None:
            if tz_str:
                tz = parse_tz(tz_str)
            else:
                tz = self.config.tz

            res = strptime_multi(
                date_string=datetime_str,
                tz=tz,
                default_format="%Y-%m-%dT%H:%M:%S.%fZ",
            )

            logger.debug(f"Converted date {datetime_str} to {res} for {path}")

            return res

        creation_time = datetime.fromtimestamp(path.stat().st_ctime, tz=self.config.tz)
        logger.warning(
            f"Could not find creation time in {path}. "
            f"Using file creation time {creation_time}. "
        )

        return creation_time
