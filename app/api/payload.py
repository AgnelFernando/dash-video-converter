from pydantic import BaseModel
from enum import Enum

class VideoEncodingStatus(Enum):
    QUEUED = 1
    PROCESSING = 2
    FAILED = 3
    SUCCESS = 4

class CreateVERequest(BaseModel):
    userId: int
    videoId: int
    hasAudio: bool
    objectKey: str
    baseUrl: str
