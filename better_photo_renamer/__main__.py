import logging
from datetime import datetime

from pillow_heif import register_heif_opener
from pytz import timezone
from rich.logging import RichHandler

from library.accessors import *  # noqa: F403
from library.apply_changes import apply_changes
from library.cache import PandasPickleCache
from library.detect_duplicate import detect_duplicate
from library.file_operator.file_operator import FILE_OPERATORS
from library.generate_filename import generate_path
from library.generate_filename.live_photos import merge_live_photos, split_live_photos
from library.grouping import parse_grouping_args
from library.grouping.grouping import group_by_metadata
from library.indexer import index_metadata
from library.load_dir import load_dir
from library.load_metadata import load_metadata
from library.metadata_editor.metadata_editor import MetadataEditorConfig

from .parser import arg_parser

args = arg_parser.parse_args()

level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(level=level, handlers=[RichHandler()])
register_heif_opener()

logger = logging.getLogger(__name__)

start = datetime.now()


paths = load_dir(args.dir, recursive=args.recursive)
metadata_config = MetadataEditorConfig(
    tz=timezone(args.tz),
    extract_content_hash=args.extract_content_hash,
)

if not paths:
    logger.info("No files found")
    exit()

metadata_cache = PandasPickleCache("metadata_cache.pkl") if args.cache else None

metadata_df = load_metadata(paths, metadata_config, cache=metadata_cache)

metadata_df, metadata_live_df = split_live_photos(metadata_df)

if args.group:
    group_args = parse_grouping_args(args.group)
    metadata_df = group_by_metadata(metadata_df, group_args)

if metadata_config.extract_content_hash:
    logger.info("Detecting duplicates")
    metadata_df["duplicate"] = detect_duplicate(metadata_df)

metadata_df = index_metadata(metadata_df)

n_files = len(metadata_df)
logger.info(f"Processing {n_files} files")

metadata_df[["new_filename", "new_path"]] = generate_path(metadata_df, args.filename)

if not metadata_live_df.empty:
    metadata_rename_df = merge_live_photos(metadata_live_df, metadata_df)
else:
    metadata_rename_df = metadata_df

if metadata_rename_df["new_path"].duplicated().any():
    duplicate_df = metadata_rename_df[metadata_rename_df["new_path"].duplicated()]
    duplicate_df["path"] = duplicate_df["path"].apply(lambda x: x.name)
    duplicate_df["new_path"] = duplicate_df["new_path"].apply(lambda x: x.name)
    logger.error(duplicate_df)
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
    metadata_editor_config=metadata_config,
    ask_confirm=args.ask_confirm,
)

logger.info(f"Finished in {datetime.now() - start}")
