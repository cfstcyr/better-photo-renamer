import pandas as pd


def explode_dict(
    df: pd.DataFrame,
    col: str,
    prefix: bool = False,
    prefix_sep: str = ".",
) -> pd.DataFrame:
    df = df[col].apply(pd.Series)

    if prefix:
        df = df.add_prefix(f"{col}{prefix_sep}")

    return df


def _split_match_exact(
    split_true: pd.DataFrame, split_false: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    match = pd.Index.intersection(split_true.index, split_false.index)

    matched_true = split_true.loc[match]
    matched_false = split_false.loc[match]
    matched_false = matched_false[~matched_false.index.duplicated(keep="first")]

    matched_true["match_index"] = matched_false.loc[match, "index"]
    matched_false["match_index"] = matched_true.loc[match, "index"]

    return matched_true, matched_false


def split_match(
    df: pd.DataFrame, split_col: str, match_col: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.reset_index()
    df.index = pd.Index(df[match_col])

    # Split the dataframe into two based on the split column
    split_true = df[df[split_col]]
    split_false = df[~df[split_col]]

    # Match the two dataframes based on the match column for exact matches
    matched_exact_true, matched_exact_false = _split_match_exact(
        split_true, split_false
    )

    # Remove the matched rows from the split dataframes
    split_true = split_true[~split_true.index.isin(matched_exact_true.index)]
    split_false = split_false[~split_false.index.isin(matched_exact_false.index)]

    # Keep only the first row for each index (duplicates are not allowed)
    unique_split_false = split_false[~split_false.index.duplicated(keep="first")]

    # Match the remaining rows based on the match column
    match = unique_split_false.index.get_indexer(split_true.index, method="nearest")

    # Insert the matched rows back into the split dataframes
    split_true["match_index"] = unique_split_false.iloc[match]["index"].values
    split_true.index = pd.Index(split_true["match_index"])
    split_false.index = pd.Index(split_false["index"])
    split_false.loc[split_true.index, "match_index"] = split_true["index"].values

    # Concat exact matches and nearest matches
    if not matched_exact_true.empty:
        split_true = pd.concat([split_true, matched_exact_true])
    if not matched_exact_false.empty:
        split_false = pd.concat([split_false, matched_exact_false])

    # Reset index
    split_true.index = pd.Index(split_true["index"])
    split_true = split_true.drop(columns=["index"])
    split_false.index = pd.Index(split_false["index"])
    split_false = split_false.drop(columns=["index"])

    return split_false, split_true
