import logging
import re
from datetime import datetime
from pathlib import Path

import ffmpeg

from library.utils.datetime import strptime_multi
from library.utils.errors import ExtractionError
from library.utils.hash import hash_dict

from .metadata_extractor import Metadata, MetadataExtractor

CREATION_TIME_TAGS = [
    "com.apple.quicktime.creationdate",
    "creation_time",
]

GPS_ISO6709_TAG = "com.apple.quicktime.location.ISO6709"
GPS_ISO6709_REGEX = (
    r"(?P<lat>[+-]\d{2}\.\d+)(?P<long>[+-]\d{3}\.\d+)(?P<alt>[+-]\d+\.\d+)?\/"
)

logger = logging.getLogger(__name__)


class MetadataExtractorMov(MetadataExtractor):
    allowed_extensions = [".mov"]

    def _extract(self, path: Path) -> Metadata:
        probe = ffmpeg.probe(path)

        lat, long = self._extract_gps_data(path, probe["format"]["tags"])

        return Metadata(
            metadata_hash=hash_dict(probe["format"]["tags"]),
            creation_time=self._extract_creation_time(path, probe["format"]["tags"]),
            is_live_photo="com.apple.quicktime.live-photo.auto"
            in probe["format"]["tags"],
            lat=lat,
            long=long,
        )

    def _extract_creation_time(self, path: Path, tags: dict):
        for tag in CREATION_TIME_TAGS:
            if tag in tags:
                return strptime_multi(
                    tags[tag],
                    tz=self.config.tz,
                    default_format="%Y-%m-%dT%H:%M:%S.%fZ",
                )

        creation_time = datetime.fromtimestamp(path.stat().st_ctime, tz=self.config.tz)
        logger.warning(
            f"Could not find creation time in {path}. "
            f"Using file creation time {creation_time}. "
        )

        return creation_time

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
        return -1, -1
