import pandas as pd
from lark import Lark

from .filename_transformer import FilenameTransformer
from .grammar import GRAMMAR

parser = Lark(GRAMMAR, parser="lalr")


def generate_filename(df: pd.DataFrame, format: str) -> pd.Series | str:
    df["index"] = pd.Index(range(len(df)))

    tree = parser.parse(format)

    res = FilenameTransformer(df).transform(tree) + df["ext"]
    res = res.rename("new_filename")

    return res


def generate_path(df: pd.DataFrame, format: str) -> pd.DataFrame:
    df["new_filename"] = generate_filename(df, format)
    df["new_path"] = df.apply(
        lambda row: row["path"].parent / row["new_filename"], axis=1
    )

    return df[["new_filename", "new_path"]]
