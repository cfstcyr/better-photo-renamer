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
