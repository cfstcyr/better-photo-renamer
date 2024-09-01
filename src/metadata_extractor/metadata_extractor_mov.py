from pathlib import Path
import ffmpeg
from src.utils.errors import ExtractionError
from src.utils.hash import hash_dict
from src.utils.datetime import strptime_multi
from .metadata_extractor import MetadataExtractor, Metadata

CREATION_TIME_TAGS = [
    "com.apple.quicktime.creationdate",
    "creation_time",
]


class MetadataExtractorMov(MetadataExtractor):
    allowed_extensions = [".mov"]

    def _extract(self, path: Path) -> Metadata:
        probe = ffmpeg.probe(path)

        datetime_tag = next(
            (tag for tag in CREATION_TIME_TAGS if tag in probe["format"]["tags"]), None
        )

        if datetime_tag is None:
            raise ExtractionError(f"Date not found in tags: {probe['format']['tags']}")

        return Metadata(
            metadata_hash=hash_dict(probe["format"]["tags"]),
            creation_time=strptime_multi(
                probe["format"]["tags"][datetime_tag],
                tz=self.config.tz,
                default_format="%Y-%m-%dT%H:%M:%S.%fZ",
            ),
            is_live_photo="com.apple.quicktime.live-photo.auto"
            in probe["format"]["tags"],
        )
