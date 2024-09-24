from typing import Protocol, TypeVar, overload

import pandas as pd

T_cov = TypeVar("T_cov", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


class TagFn(Protocol):
    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.Series | str: ...


class TagInnerFn(Protocol[T_contra]):
    def __call__(self, series: T_contra, *args, **kwargs) -> pd.Series | str: ...


class TransformFn(Protocol[T_cov]):
    def __call__(self, df: pd.DataFrame) -> T_cov: ...


@overload
def tag_fn_wrapper(
    col_or_transform_fn: str, inner_fn: TagInnerFn[pd.Series]
) -> TagFn: ...
@overload
def tag_fn_wrapper(
    col_or_transform_fn: TransformFn[pd.Series],
    inner_fn: TagInnerFn[pd.Series],
) -> TagFn: ...
@overload
def tag_fn_wrapper(
    col_or_transform_fn: TransformFn[pd.DataFrame],
    inner_fn: TagInnerFn[pd.DataFrame],
) -> TagFn: ...
def tag_fn_wrapper(
    col_or_transform_fn: str | TransformFn, inner_fn: TagInnerFn
) -> TagFn:
    def tag_fn_wrapper(df: pd.DataFrame, *args, **kwargs) -> pd.Series | str:
        if callable(col_or_transform_fn):
            return inner_fn(col_or_transform_fn(df), *args, **kwargs)

        return inner_fn(df[col_or_transform_fn], *args, **kwargs)

    return tag_fn_wrapper
