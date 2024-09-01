from typing import Any

import pandas as pd
from lark import Transformer

from .tag_fn import TAGS


class FilenameTransformer(Transformer[Any, str | pd.Series]):
    df: pd.DataFrame

    def __init__(self, df: pd.DataFrame, visit_tokens: bool = True) -> None:
        super().__init__(visit_tokens)
        self.df = df

    def start(self, items):
        res = ""

        for item in items:
            res += item.astype("str") if isinstance(item, pd.Series) else str(item)

        return res

    def tag(self, items):
        (tag,) = items

        return TAGS[tag](self.df)

    def tag_params(self, items):
        tag, args = items

        args_dict = {k: v for k, v in args.items() if isinstance(k, int)}
        kwargs_dict = {k: v for k, v in args.items() if isinstance(k, str)}

        return TAGS[tag](self.df, *args_dict.values(), **kwargs_dict)

    def params_v(self, items):
        curr, next = items

        if not next:
            return {0: curr}

        keys = [k for k in next.keys() if isinstance(k, int)]

        if not keys:
            return {**next, 0: curr}

        index = max(k for k in next.keys() if isinstance(k, int)) + 1

        return {**next, index: curr}

    def params_k(self, items):
        curr, next = items

        return {**curr, **next} if next else curr

    def param_k(self, items):
        key, value = items

        return {key: value}

    def STRING(self, items):
        return items[1:-1]

    def NUMBER(self, items):
        return int(items)

    def NAME(self, items):
        return items.value
