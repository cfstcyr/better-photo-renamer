from datetime import datetime
from typing import TypedDict


class Metadata(TypedDict):
    id: str
    creation_time: datetime
    is_live_photo: bool
