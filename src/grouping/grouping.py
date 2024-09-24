import logging

import pandas as pd

from src.grouping.grouping_transformer import GroupingArgs

from .grouping_methods import GROUPING_METHODS

logger = logging.getLogger(__name__)


def group_by_metadata(
    metadata_df: pd.DataFrame, grouping_args: GroupingArgs
) -> pd.DataFrame:
    if grouping_args.method not in GROUPING_METHODS:
        raise ValueError(f"Unknown grouping method {grouping_args.method}")

    for group in grouping_args.group_cols:
        if group not in metadata_df.columns:
            raise ValueError(f"Unknown metadata column {group}")

    logger.info(
        f"Grouping by {grouping_args.group_cols} using [blue bold]{grouping_args.method}[/blue bold]",
        extra={"markup": True},
    )

    return GROUPING_METHODS[grouping_args.method](
        metadata_df, grouping_args.group_cols, **grouping_args.params
    )
