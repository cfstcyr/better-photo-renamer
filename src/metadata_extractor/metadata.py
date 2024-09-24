from datetime import datetime
from typing import TypedDict


class Metadata(TypedDict):
    metadata_hash: str
    creation_time: datetime
    is_live_photo: bool
    lat: float
    long: float
