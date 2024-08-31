from lark import Lark
import pandas as pd

from .filename_transformer import FilenameTransformer
from .grammar import GRAMMAR


def generate_filename(df: pd.DataFrame, format: str) -> pd.Series | str:
    df["index"] = pd.Index(range(len(df)))

    p = Lark(GRAMMAR, parser="lalr")
    tree = p.parse(format)

    res = FilenameTransformer(df).transform(tree) + df["ext"]
    res = res.rename("new_filename")

    return res
