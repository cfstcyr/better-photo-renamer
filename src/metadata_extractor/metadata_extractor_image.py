import logging
from datetime import datetime
from pathlib import Path
from pprint import pprint

import piexif
from PIL import Image

from src.utils.datetime import strptime_multi
from src.utils.gps import convert_gps_to_decimal
from src.utils.hash import hash_dict

from .metadata_extractor import Metadata, MetadataExtractor

codec = "ISO-8859-1"  # or latin-1


logger = logging.getLogger(__name__)


def exif_to_tag(exif_dict):
    exif_tag_dict = {}

    for ifd in exif_dict:
        if exif_dict[ifd] is None:
            continue

        exif_tag_dict[ifd] = {}

        for tag in exif_dict[ifd]:
            try:
                element = exif_dict[ifd][tag].decode(codec)

            except AttributeError:
                element = exif_dict[ifd][tag]

            exif_tag_dict[ifd][piexif.TAGS[ifd][tag]["name"]] = element

    return exif_tag_dict


class MetadataExtractorImage(MetadataExtractor):
    allowed_extensions = [".jpg", ".jpeg", ".png", ".heic"]

    def _extract(self, path: Path) -> Metadata:
        img = Image.open(path)
        tags = exif_to_tag(piexif.load(img.info.get("exif")))

        return Metadata(
            metadata_hash=hash_dict(tags),
            creation_time=self._extract_creation_time(path, tags),
            is_live_photo=False,
            gps_latitude=convert_gps_to_decimal(tags["GPS"]["GPSLatitude"])
            if self._has_gps_data(tags)
            else -1,
            gps_longitude=convert_gps_to_decimal(tags["GPS"]["GPSLongitude"])
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
