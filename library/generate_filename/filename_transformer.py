import logging
from typing import Any

import pandas as pd
from lark import Transformer

from .tag_fn import TAGS

logger = logging.getLogger(__name__)


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

        logger.info(f"Executing tag <{tag}>")

        return TAGS[tag](self.df)

    def tag_params(self, items):
        tag, args = items

        args_list = list({k: v for k, v in args.items() if isinstance(k, int)}.values())
        args_list.reverse()
        kwargs_dict = {k: v for k, v in args.items() if isinstance(k, str)}

        logger.info(
            f"Executing tag <{tag}:{",".join(args_list)}{"," if args_list and kwargs_dict else ""}{",".join(f"{key}={value}" for key, value in kwargs_dict.items())}>"
        )

        return TAGS[tag](self.df, *args_list, **kwargs_dict)

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
