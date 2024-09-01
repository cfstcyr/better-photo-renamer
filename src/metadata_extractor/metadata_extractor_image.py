from datetime import datetime
import logging
from pathlib import Path

from .metadata_extractor import MetadataExtractor, Metadata
from src.utils.hash import hash_dict
from src.utils.datetime import strptime_multi
from PIL import Image
from PIL.ExifTags import TAGS


logger = logging.getLogger(__name__)


class MetadataExtractorImage(MetadataExtractor):
    allowed_extensions = [".jpg", ".jpeg", ".png", ".heic"]

    def _extract(self, path: Path) -> Metadata:
        img = Image.open(path)

        tags_exif = img.getexif()
        tags = {TAGS[k]: v for k, v in tags_exif.items() if k in TAGS}

        date_str = (
            tags["DateTimeOriginal"]
            if "DateTimeOriginal" in tags
            else tags["DateTime"]
            if "DateTime" in tags
            else None
        )

        if date_str is not None:
            creation_time = strptime_multi(
                date_str, tz=self.config.tz, default_format="%Y:%m:%d %H:%M:%S"
            )
        else:
            creation_time = datetime.fromtimestamp(
                path.stat().st_ctime, tz=self.config.tz
            )
            logger.warning(
                f"Could not find creation time in {path}. "
                f"Using file creation time {creation_time}. "
            )

        return Metadata(
            metadata_hash=hash_dict(tags),
            creation_time=creation_time,
            is_live_photo=False,
        )
