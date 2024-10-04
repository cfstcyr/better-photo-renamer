import logging

from pillow_heif import register_heif_opener
from pytz import timezone
from rich.logging import RichHandler

from library.cache import PandasPickleCache
from library.generate_filename.live_photos import split_live_photos
from library.load_dir import load_dir
from library.load_metadata import load_metadata
from library.match_medias import (
    euclidean_distance_calculator,
    match_medias_all,
    normalized_euclidean_distance_calculator,
    np_cosine_distance_calculator,
)
from library.metadata_editor.metadata_editor import MetadataEditorConfig

from .parser import arg_parser

args = arg_parser.parse_args()

level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(level=level, handlers=[RichHandler()])
register_heif_opener()

logger = logging.getLogger(__name__)

paths = load_dir(args.dir, recursive=args.recursive)
metadata_config = MetadataEditorConfig(
    tz=timezone(args.tz),
    extract_content_hash=True,
)

if not paths:
    logger.info("No files found")
    exit()

metadata_cache = PandasPickleCache("metadata_cache.pkl") if args.cache else None

metadata_df = load_metadata(paths, metadata_config, cache=metadata_cache)
metadata_df["name"] = metadata_df["path"].apply(lambda x: x.name)

if not args.include_live_photos:
    metadata_df, _ = split_live_photos(metadata_df)

metadata_df = metadata_df.set_index("name")
metadata_df["timestamp"] = metadata_df["creation_time"].astype(int)

metadata_without_gps = metadata_df[metadata_df["lat"].isna()]

if metadata_without_gps.empty:
    logger.info("No photos without GPS found")
    exit()

logger.info(f"Found {len(metadata_without_gps)} photos without GPS")


matched_medias = match_medias_all(
    distance_calculators={
        "content_hash": np_cosine_distance_calculator,
        "timestamp": euclidean_distance_calculator,
    },
    result_distance_calculator=normalized_euclidean_distance_calculator,
    medias=metadata_without_gps.dropna(subset=["content_hash"]),
    medias_match=metadata_df.dropna(subset=["content_hash"]),
)

print(matched_medias)
