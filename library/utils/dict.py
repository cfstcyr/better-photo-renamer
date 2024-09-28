from typing import Any, TypeVar, overload

T = TypeVar("T")


@overload
def get_dict_value(d: dict, key: str) -> None | Any: ...
@overload
def get_dict_value(d: dict, key: str, default: T) -> T: ...
def get_dict_value(d: dict, key: str, default: T | None = None) -> None | T | Any:
    curr, rest = key.split(".", 1) if "." in key else (key, None)

    if curr not in d:
        return default

    if rest is None:
        return d[curr]

    return (
        get_dict_value(d[curr], rest, default) if isinstance(d[curr], dict) else default
    )
