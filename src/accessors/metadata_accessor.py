import pandas as pd

from src.metadata_extractor import Metadata


@pd.api.extensions.register_dataframe_accessor("metadata")
class MetadataAccessor:
    def __init__(self, pandas_obj: pd.DataFrame):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if not all(
            col in obj.columns
            for col in ["path"] + [field for field in Metadata.__annotations__.keys()]
        ):
            raise AttributeError("Must have columns 'path' and all metadata fields")
