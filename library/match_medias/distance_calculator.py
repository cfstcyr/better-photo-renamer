from typing import Generic, Protocol, TypeVar

import numpy as np
import pandas as pd

from library.utils.series import SeriesBound

T = TypeVar("T", bound=SeriesBound)
S = TypeVar("S", bound=SeriesBound)


class DistanceCalculatorN(Protocol, Generic[T, S]):
    def __call__(self, *vectors: "pd.Series[T]") -> "pd.Series[S]": ...


class DistanceCalculator2(Protocol, Generic[T, S]):
    def __call__(
        self, vector1: "pd.Series[T]", vector2: "pd.Series[T]"
    ) -> "pd.Series[S]": ...


def euclidean_distance_calculator(*vectors: pd.Series) -> pd.Series:
    return pd.Series(
        np.linalg.norm(
            np.array(vectors).T,
            axis=1,
        ),
        index=vectors[0].index,
    )


def normalized_euclidean_distance_calculator(*vectors: pd.Series) -> pd.Series:
    return euclidean_distance_calculator(
        *((vector - vector.mean()) / vector.std() for vector in vectors)
    )


def np_cosine_similarity_calculator(
    vector1: "pd.Series[np.ndarray]",  # type: ignore
    vector2: "pd.Series[np.ndarray]",  # type: ignore
) -> "pd.Series[float]":
    vector1_np = np.array(vector1.values.tolist())
    vector2_np = np.array(vector2.values.tolist())

    dot_product = np.sum(vector1_np * vector2_np, axis=1)
    norm_vector1 = np.linalg.norm(vector1_np, axis=1)
    norm_vector2 = np.linalg.norm(vector2_np, axis=1)

    cosine_similarity = dot_product / (norm_vector1 * norm_vector2)

    return pd.Series(cosine_similarity, index=vector1.index)


def np_cosine_distance_calculator(
    vector1: "pd.Series[np.ndarray]",  # type: ignore
    vector2: "pd.Series[np.ndarray]",  # type: ignore
) -> "pd.Series[float]":
    return 1 - np_cosine_similarity_calculator(vector1, vector2)


if __name__ == "__main__":
    s1 = pd.Series([1, 2, 3], name="s1")
    s2 = pd.Series([4, 5, 6], name="s2")
