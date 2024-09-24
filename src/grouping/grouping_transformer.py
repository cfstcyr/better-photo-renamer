from typing import Any

from lark import Token, Transformer

from .grouping_args import GroupingArgs
from .grouping_methods import GROUPING_METHODS


class GroupingTransformer(Transformer[Any, GroupingArgs]):
    def struct_default(self, items):
        return GroupingArgs(
            method="exact",
            group_cols=items[0],
        )

    def struct_params(self, items):
        method, group_cols, params = items

        return GroupingArgs(
            method=method,
            group_cols=group_cols,
            params=params or {},
        )

    def method(self, item: list[str]) -> str:
        method = item[0]

        if method not in GROUPING_METHODS:
            raise ValueError(f"Unknown grouping method {method}.")

        return method

    def group_cols(self, items: list) -> list[str]:
        col, rest = items

        if rest:
            return [col, *rest]
        else:
            return [col]

    def params(self, items) -> dict:
        params, rest = items

        if rest:
            params = {**params, **rest}

        return params

    def key_value(self, items: list[str]) -> dict:
        key, value = items

        return {key: value}

    def STRING(self, items: Token) -> str:
        return items.value

    def NUMBER(self, items: Token):
        return int(items)
