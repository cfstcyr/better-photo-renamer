import logging

from pillow_heif import register_heif_opener
from pytz import timezone
from rich.logging import RichHandler

from src.file_operator.file_operator import FILE_OPERATORS
from src.grouping import parse_grouping_args
from src.grouping.grouping import group_by_metadata

from .accessors import *  # noqa: F403
from .apply_changes import apply_changes
from .generate_filename import generate_path
from .generate_filename.live_photos import merge_live_photos, split_live_photos
from .load_dir import load_dir
from .load_metadata import load_metadata
from .metadata_extractor.metadata_extractor import MetadataExtractorConfig
from .parser import arg_parser

logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
register_heif_opener()

logger = logging.getLogger(__name__)

args = arg_parser.parse_args()

paths = load_dir(args.dir, recursive=args.recursive)
metadata_config = MetadataExtractorConfig(tz=timezone(args.tz))

if not paths:
    logger.info("No files found")
    exit()

metadata_df = load_metadata(paths, metadata_config)

if args.group:
    group_args = parse_grouping_args(args.group)
    metadata_df = group_by_metadata(metadata_df, group_args)

n_files = len(metadata_df)
logger.info(f"Processing {n_files} files")

metadata_df, metadata_live_df = split_live_photos(metadata_df)
metadata_df[["new_filename", "new_path"]] = generate_path(metadata_df, args.filename)

if not metadata_live_df.empty:
    metadata_rename_df = merge_live_photos(metadata_live_df, metadata_df)
else:
    metadata_rename_df = metadata_df

if metadata_rename_df["new_path"].duplicated().any():
    raise ValueError("Duplicate paths")

metadata_rename_df = metadata_rename_df[
    metadata_rename_df["path"] != metadata_rename_df["new_path"]
]

metadata_rename_df = metadata_rename_df.sort_values(by="path")

logger.info(
    f"Renaming {len(metadata_rename_df)} files ({n_files - len(metadata_rename_df)} files are already correctly named)"
)

if len(metadata_rename_df) == 0:
    logger.info("No files to rename")
    exit()

apply_changes(
    paths=metadata_rename_df["path"],
    new_paths=metadata_rename_df["new_path"],
    file_operator=FILE_OPERATORS[args.operator],
    ask_confirm=args.ask_confirm,
)
