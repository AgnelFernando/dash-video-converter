from sqlalchemy.orm import Session

from . import models
from api import payload

def create_video_encoding_request(db: Session, req: payload.CreateVERequest):
    db_req = models.VideoEncodingRequest()
    
    db_req.user_id = req.userId
    db_req.video_id = req.videoId
    db_req.has_audio = req.hasAudio
    db_req.object_key = req.objectKey
    db_req.base_url = req.baseUrl
    db_req.status = payload.VideoEncodingStatus.QUEUED
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req


def get_video_encoding_request_by_id(db: Session, id: int):
    return db.query(models.VideoEncodingRequest).filter(models.VideoEncodingRequest.id == id).first()


def update_vp_request_status(db: Session, 
                            req: models.VideoEncodingRequest, 
                            status: payload.VideoEncodingStatus):
    req.status = status     
    db.commit()
    db.refresh(req) 


def update_ve_request_by_id(db: Session, 
                            id: int, 
                            status: payload.VideoEncodingStatus):
    req = get_video_encoding_request_by_id(db, id)       
    if req is not None:
        update_vp_request_status(db, req, status)     
                           


