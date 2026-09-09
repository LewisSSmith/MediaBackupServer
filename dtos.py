import datetime
import uuid
from dataclasses import dataclass


@dataclass
class FileDataDTO:
    id: uuid.UUID
    hash: str
    filename: str
    mime: str
    size: int
    date_uploaded: datetime.datetime
    date_created: datetime.datetime
    date_last_modified: datetime.datetime
    metadata: dict

@dataclass
class LocationDTO:
    id: uuid.UUID
    latitude: float
    longitude: float
