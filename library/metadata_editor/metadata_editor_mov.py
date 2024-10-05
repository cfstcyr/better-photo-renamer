import logging
import re
from datetime import datetime
from pathlib import Path

import ffmpeg
import numpy as np

from library.utils.errors import ExtractionError
from library.utils.hash import hash_dict

from .metadata_editor import Metadata, MetadataEditor

GPS_ISO6709_TAG = "com.apple.quicktime.location.ISO6709"
GPS_ISO6709_REGEX = (
    r"(?P<lat>[+-]\d{2}\.\d+)(?P<long>[+-]\d{3}\.\d+)(?P<alt>[+-]\d+\.\d+)?\/"
)

logger = logging.getLogger(__name__)


class MetadataEditorMov(MetadataEditor):
    _allowed_extensions = [".mov"]
    _creation_time_keys = ["com.apple.quicktime.creationdate", "creation_time"]

    def _extract(self, path: Path) -> Metadata:
        probe = ffmpeg.probe(path)

        lat, long = self._extract_gps_data(path, probe["format"]["tags"])

        return Metadata(
            metadata_hash=hash_dict(probe["format"]["tags"]),
            content_hash=None,
            creation_time=self._extract_creation_time(path, probe["format"]["tags"]),
            is_live_photo="com.apple.quicktime.live-photo.auto"
            in probe["format"]["tags"],
            lat=lat,
            long=long,
        )

    def _extract_creation_time(self, path: Path, tags: dict) -> datetime:
        for creation_time_key in self._creation_time_keys:
            if creation_time_key in tags:
                return super()._extract_creation_time(path, tags[creation_time_key])

        return super()._extract_creation_time(path, None)

    def _extract_gps_data(self, path: Path, tags: dict) -> tuple[float, float]:
        if GPS_ISO6709_TAG in tags:
            gps_data = re.match(GPS_ISO6709_REGEX, tags[GPS_ISO6709_TAG])
            if gps_data:
                return float(gps_data.group("lat")), float(gps_data.group("long"))
            else:
                raise ExtractionError(
                    f"Could not extract GPS data from {tags[GPS_ISO6709_TAG]}"
                )

        logger.warning(f"No GPS data found in {path}")
        return np.nan, np.nan
