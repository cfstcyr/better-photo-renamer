from .tag_fn import TAGS

GRAMMAR = rf"""
    ?start: (NAME | tag)+

    ?tag: "<" TAG ">"               -> tag
        | "<" TAG ":" params ">"    -> tag_params

    ?params: params_v | params_k
    ?params_v: param_v ["," (params_v | params_k)]  -> params_v
    ?params_k: param_k ["," params_k]               -> params_k

    ?param_v: STRING | NUMBER
    ?param_k: NAME "=" param_v  -> param_k

    NAME: /([A-Za-z0-9]| |-|_)+/
    TAG: {" | ".join(map(lambda tag: f"\"{tag}\"", TAGS.keys()))}

    %import common.ESCAPED_STRING   -> STRING
    %import common.NUMBER
    %import common.WS

    %ignore WS
"""
