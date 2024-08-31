from abc import ABC, abstractmethod
from typing import Any, Optional
import pandas as pd


class Cache(ABC):
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set the value for the given key in the cache.

        Parameters:
        - key (str): The key to set the value for.
        - value (Any): The value to be set.

        Returns:
        - None
        """
        ...

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve the value associated with the given key from the cache.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            Optional[Any]: The value associated with the key, or None if the key is not found in the cache.
        """
        ...

    @abstractmethod
    def has(self, key: str) -> bool:
        """
        Check if the cache contains a value for the given key.

        Args:
            key (str): The key to check for.

        Returns:
            bool: True if the key is present in the cache, False otherwise.
        """
        ...


class PandasCache(Cache):
    @abstractmethod
    def _load(self) -> pd.DataFrame:
        """
        Load the data from the cache file and return it as a pandas DataFrame.

        Returns:
            pd.DataFrame: The loaded data as a pandas DataFrame.
        """
        ...

    @abstractmethod
    def _save(self, df: pd.DataFrame) -> None:
        """
        Save the DataFrame to a file.

        Parameters:
            df (pd.DataFrame): The DataFrame to be saved.

        Returns:
            None
        """
        ...

    def set(self, key: str, value: Any) -> None:
        df = self._load()
        df.loc[key] = pd.Series([value], index=["value"])
        self._save(df)

    def get(self, key: str) -> Optional[Any]:
        df = self._load()

        return df.loc[key]["value"] if key in df.index else None

    def has(self, key: str) -> bool:
        df = self._load()
        return key in df.index


class PandasPickleCache(PandasCache):
    _path: str
    _df: Optional[pd.DataFrame] = None

    def __init__(self, path: str):
        self._path = path

    def _load(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df

        try:
            self._df = pd.read_pickle(self._path)
            return self._df
        except FileNotFoundError:
            return pd.DataFrame(columns=["value"])

    def _save(self, df: pd.DataFrame) -> None:
        self._df = df
        df.to_pickle(self._path)
