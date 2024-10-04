from datetime import datetime
from typing import TypedDict

import numpy as np


class Metadata(TypedDict):
    metadata_hash: str
    content_hash: np.ndarray | None
    creation_time: datetime
    is_live_photo: bool
    lat: float
    long: float
