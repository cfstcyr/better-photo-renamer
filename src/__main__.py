import logging

import pandas as pd
from pillow_heif import register_heif_opener
from pytz import timezone

from .accessors import *  # noqa: F403
from .generate_filename import generate_filename
from .load_dir import load_dir
from .load_metadata import load_metadata
from .metadata_extractor.metadata_extractor import MetadataExtractorConfig
from .parser import arg_parser
from .rename_files import rename_files
from .utils.df import split_match

logging.basicConfig(level=logging.INFO)
register_heif_opener()

logger = logging.getLogger(__name__)

args = arg_parser.parse_args()

paths = load_dir(args.dir, recursive=args.recursive)
metadata_config = MetadataExtractorConfig(tz=timezone(args.tz))

metadata_df = load_metadata(paths, metadata_config)

metadata_df, metadata_live_df = split_match(
    metadata_df, split_col="is_live_photo", match_col="creation_time"
)

metadata_df["new_filename"] = generate_filename(metadata_df, args.filename)
metadata_df["new_path"] = metadata_df.apply(
    lambda row: row["path"].parent / row["new_filename"], axis=1
)

metadata_live_df = pd.merge(
    left=metadata_live_df,
    right=metadata_df[["new_path"]],
    left_on="match_index",
    right_index=True,
)
metadata_live_df["new_path"] = metadata_live_df.apply(
    lambda row: row["path"].parent / f"{row['new_path'].stem}_live{row['path'].suffix}",
    axis=1,
)

metadata_rename_df = pd.concat(
    [metadata_df[["path", "new_path"]], metadata_live_df[["path", "new_path"]]]
)

if metadata_rename_df["new_path"].duplicated().any():
    raise ValueError("Duplicate paths")

n_files = len(metadata_rename_df)
logger.info(f"Processing {n_files} files")

metadata_rename_df = metadata_rename_df[
    metadata_rename_df["path"] != metadata_rename_df["new_path"]
]

logger.info(
    f"Renaming {len(metadata_rename_df)} files ({n_files - len(metadata_rename_df)} files are already correctly named)"
)

rename_files(
    paths=metadata_rename_df["path"],
    new_paths=metadata_rename_df["new_path"],
)
