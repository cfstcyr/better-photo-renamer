import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import piexif
from PIL import Image

from library.utils.exif import exif_to_tag
from library.utils.gps import convert_gps_to_decimal
from library.utils.hash import hash_dict

from .metadata_editor import Metadata, MetadataEditor

logger = logging.getLogger(__name__)


class MetadataEditorImage(MetadataEditor):
    _allowed_extensions = [".jpg", ".jpeg", ".png", ".heic"]

    def _extract(self, path: Path) -> Metadata:
        img = Image.open(path)

        try:
            tags = exif_to_tag(piexif.load(img.info.get("exif")))

            metadata_hash = hash_dict(tags)
            lat, long = self._extract_gps_data(path, tags)
            creation_time = self._extract_creation_time(path, tags)
        except Exception as e:
            logger.warning(f"Could not extract metadata from EXIF for '{path}': {e}")
            logger.info(f"Replacing metadata by default values for '{path}'")

            metadata_hash = ""
            lat, long = self._extract_gps_data(path, {})
            creation_time = self._extract_creation_time(path, {})

        content_hash = (
            self._extract_content_hash(path, img)
            if self.config.extract_content_hash
            else None
        )

        return Metadata(
            metadata_hash=metadata_hash,
            content_hash=content_hash,
            creation_time=creation_time,
            is_live_photo=False,
            lat=lat,
            long=long,
        )

    def _extract_creation_time(self, path: Path, tags: dict) -> datetime:
        datetime_str = tags.get("0th", {}).get("DateTime")
        offset_time_str = tags.get("Exif", {}).get("OffsetTime")

        return super()._extract_creation_time(path, datetime_str, offset_time_str)

    def _extract_gps_data(self, path: Path, tags: dict) -> tuple[float, float]:
        if self._has_gps_data(tags):
            return (
                convert_gps_to_decimal(tags["GPS"]["GPSLatitude"]),
                convert_gps_to_decimal(tags["GPS"]["GPSLongitude"]),
            )

        logger.warning(f"No GPS data found in {path}")
        return np.nan, np.nan

    def _extract_content_hash(self, path: Path, img: Image.Image) -> np.ndarray:
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        img = img.convert("L")

        pixel_data = list(img.getdata())  # type: ignore
        avg_pixel = sum(pixel_data) / len(pixel_data)

        return np.fromiter((1 if pixel > avg_pixel else 0 for pixel in pixel_data), int)

    def _has_gps_data(self, tags: dict):
        return (
            "GPS" in tags
            and "GPSLatitude" in tags["GPS"]
            and "GPSLongitude" in tags["GPS"]
        )
