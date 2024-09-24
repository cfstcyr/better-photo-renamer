GROUPING_GRAMMAR = r"""
    ?start: struct
        
    ?struct: group_cols                         -> struct_default
        | method ":" group_cols [":" params]    -> struct_params

    ?method: STRING -> method
    ?group_cols: STRING ["," group_cols] -> group_cols

    ?params: key_value ["," params] -> params
    ?key_value: STRING "=" value  -> key_value
    ?value: STRING | NUMBER

    STRING: /[a-zA-Z_]+/
    %import common.NUMBER
"""
