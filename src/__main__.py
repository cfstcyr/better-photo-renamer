import logging

from pillow_heif import register_heif_opener
from pytz import timezone
from rich import print as rprint
from rich.logging import RichHandler

from .accessors import *  # noqa: F403
from .generate_filename import generate_path
from .generate_filename.live_photos import merge_live_photos, split_live_photos
from .load_dir import load_dir
from .load_metadata import load_metadata
from .metadata_extractor.metadata_extractor import MetadataExtractorConfig
from .parser import arg_parser
from .rename_files import rename_files

logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
register_heif_opener()

logger = logging.getLogger(__name__)

args = arg_parser.parse_args()

print(args)

paths = load_dir(args.dir, recursive=args.recursive)
metadata_config = MetadataExtractorConfig(tz=timezone(args.tz))

metadata_df = load_metadata(paths, metadata_config)

n_files = len(metadata_df)
logger.info(f"Processing {n_files} files")

metadata_df, metadata_live_df = split_live_photos(metadata_df)
metadata_df[["new_filename", "new_path"]] = generate_path(metadata_df, args.filename)
metadata_rename_df = merge_live_photos(metadata_live_df, metadata_df)

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

rename_files(
    paths=metadata_rename_df["path"],
    new_paths=metadata_rename_df["new_path"],
    ask_confirm=args.ask_confirm,
    dry_run=args.dry_run,
)