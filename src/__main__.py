from pprint import pprint
from pytz import timezone

from .accessors import *  # noqa: F403

from .metadata_extractor.metadata_extractor import MetadataExtractorConfig
from .parser import arg_parser
from .load_dir import load_dir
from .load_metadata import load_metadata
from pillow_heif import register_heif_opener
from .utils.df import split_match
from .generate_filename import generate_filename

register_heif_opener()

args = arg_parser.parse_args()

paths = load_dir(args.dir)
metadata_config = MetadataExtractorConfig(tz=timezone(args.tz))

metadata_df = load_metadata(paths, metadata_config)

metadata_df, metadata_live_df = split_match(
    metadata_df, split_col="is_live_photo", match_col="creation_time"
)

metadata_df["new_filename"] = generate_filename(metadata_df, args.filename)

pprint(metadata_df["new_filename"].tolist())
