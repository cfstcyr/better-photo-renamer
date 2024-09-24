import logging
from datetime import datetime
from pathlib import Path

import piexif
from PIL import Image

from src.utils.datetime import strptime_multi
from src.utils.exif import exif_to_tag
from src.utils.gps import convert_gps_to_decimal
from src.utils.hash import hash_dict

from .metadata_extractor import Metadata, MetadataExtractor

logger = logging.getLogger(__name__)


class MetadataExtractorImage(MetadataExtractor):
    allowed_extensions = [".jpg", ".jpeg", ".png", ".heic"]

    def _extract(self, path: Path) -> Metadata:
        img = Image.open(path)
        tags = exif_to_tag(piexif.load(img.info.get("exif")))

        return Metadata(
            metadata_hash=hash_dict(tags),
            creation_time=self._extract_creation_time(path, tags),
            is_live_photo=False,
            lat=convert_gps_to_decimal(tags["GPS"]["GPSLatitude"])
            if self._has_gps_data(tags)
            else -1,
            long=convert_gps_to_decimal(tags["GPS"]["GPSLongitude"])
            if self._has_gps_data(tags)
            else -1,
        )

    def _extract_creation_time(self, path: Path, tags: dict):
        if "DateTime" in tags["0th"]:
            creation_time = strptime_multi(
                tags["0th"]["DateTime"],
                tz=self.config.tz,
                default_format="%Y:%m:%d %H:%M:%S",
            )
        else:
            creation_time = datetime.fromtimestamp(
                path.stat().st_ctime, tz=self.config.tz
            )
            logger.warning(
                f"Could not find creation time in {path}. "
                f"Using file creation time {creation_time}. "
            )

        return creation_time

    def _has_gps_data(self, tags: dict):
        return (
            "GPS" in tags
            and "GPSLatitude" in tags["GPS"]
            and "GPSLongitude" in tags["GPS"]
        )
