import logging
from pathlib import Path

import piexif
from PIL import Image

from library.utils.exif import exif_to_tag
from library.utils.gps import convert_gps_to_decimal
from library.utils.hash import hash_dict

from .metadata_extractor import Metadata, MetadataExtractor

logger = logging.getLogger(__name__)


class MetadataExtractorImage(MetadataExtractor):
    _allowed_extensions = [".jpg", ".jpeg", ".png", ".heic"]
    _creation_time_keys = ["0th.DateTime"]

    def _extract(self, path: Path) -> Metadata:
        img = Image.open(path)
        tags = exif_to_tag(piexif.load(img.info.get("exif")))

        lat, long = self._extract_gps_data(path, tags)

        return Metadata(
            metadata_hash=hash_dict(tags),
            creation_time=self._extract_creation_time(path, tags),
            is_live_photo=False,
            lat=lat,
            long=long,
        )

    def _extract_gps_data(self, path: Path, tags: dict) -> tuple[float, float]:
        if self._has_gps_data(tags):
            return (
                convert_gps_to_decimal(tags["GPS"]["GPSLatitude"]),
                convert_gps_to_decimal(tags["GPS"]["GPSLongitude"]),
            )

        logger.warning(f"No GPS data found in {path}")
        return -1, -1

    def _has_gps_data(self, tags: dict):
        return (
            "GPS" in tags
            and "GPSLatitude" in tags["GPS"]
            and "GPSLongitude" in tags["GPS"]
        )
