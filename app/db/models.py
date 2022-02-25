import datetime
from sqlalchemy import Boolean, Column, Integer, String, Enum, DateTime

from api.payload import VideoEncodingStatus

from .database import Base

class VideoEncodingRequest(Base):
    __tablename__ = "video_encoding_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    video_id = Column(Integer)
    has_audio = Column(Boolean)
    object_key = Column(String)
    base_url = Column(String)
    status = Column(Enum(VideoEncodingStatus))
    createdOn = Column(DateTime, default=datetime.datetime.utcnow)
    tdir = Column(String, default=None)
    toutdir = Column(String, default=None)

    def __str__(self) -> str:
        return str(self.__dict__)
