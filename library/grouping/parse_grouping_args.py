from lark import Lark

from .grammar import GROUPING_GRAMMAR
from .grouping_args import GroupingArgs
from .grouping_transformer import GroupingTransformer


def parse_grouping_args(str_args: str) -> GroupingArgs:
    parser = Lark(GROUPING_GRAMMAR, parser="lalr")

    return GroupingTransformer().transform(parser.parse(str_args))
