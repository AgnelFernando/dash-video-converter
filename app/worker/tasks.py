import os, subprocess, shutil, tempfile
from db import models
from celery import Task
import requests
import boto3

from api.payload import VideoEncodingStatus
from db import crud
from db.database import SessionLocal

from .celery import app


otherParams = [{"name":"720p", "video_width":1280, "kbPerSec":'3000k'},
               {"name":"360p", "video_width":640, "kbPerSec":'600k'}]

# constants
ORIGINAL_FILE_NAME = "original"                   
DASH_MPD_FILE_NAME = "dash.mpd"
VIDEO_THUMBNAIL_FILE_NAME = "preview.jpg"

# AWS env variables
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_INPUT_BUCKET = os.environ.get("S3_INPUT_BUCKET")
S3_OUTPUT_BUCKET = os.environ.get("S3_OUTPUT_BUCKET")
S3_THUMBNAIL_OUTPUT_BUCKET = os.environ.get("S3_THUMBNAIL_OUTPUT_BUCKET")

# MAIN API env variables
MAIN_API_ENDPOINT = os.environ.get("MAIN_API_ENDPOINT")
MAIN_API_KEY = os.environ.get("MAIN_API_KEY")

class DatabaseTask(Task):
    _db = None

    def before_start(self, status, retval, task_id, args, kwargs, einfo):
        if self._db is None:
            self._db = SessionLocal()

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if self._db is not None:
            self._db.close()
            self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db



@app.task(base=DatabaseTask, bind=True, priority=0)
def create_initial_dash(self, id):
    db = create_initial_dash.db
    tdir = None
    try:
        eReq = crud.get_video_encoding_request_by_id(db, id) 
        if eReq is None:
            raise
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID , 
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        tdir = tempfile.mkdtemp(prefix='video')
        input = os.path.join(tdir, ORIGINAL_FILE_NAME)
        s3.download_file(S3_INPUT_BUCKET, eReq.object_key, input)
        
        # create 720p encoded video
        cmd = get_ffmpeg_cmd(input, tdir, 0)
        subprocess.check_call(cmd, shell=True)

        # create MPEG-DASH
        outputDir = os.path.join(tdir, eReq.object_key)
        eReq.tdir = tdir
        eReq.toutdir = outputDir
        cmd = get_dash_cmd(input, eReq, [0])
        subprocess.check_call(cmd, shell=True)
        
        # upload mpeg-dash folder to s3
        subprocess.check_call(get_aws_sync_command(eReq), shell=True)       

        # create video thumbnail
        thumbnailPath = create_video_thumbnail(tdir)
        s3.upload_file(thumbnailPath, S3_THUMBNAIL_OUTPUT_BUCKET, str(eReq.video_id))

        crud.update_vp_request_status(db, eReq, VideoEncodingStatus.SUCCESS)
        
        send_video_processing_result(self.request.id, eReq.status)
        return id
    except Exception as e:
        print(f"error processing encoding request {id} err={e}")
        status = VideoEncodingStatus.FAILED
        crud.update_ve_request_by_id(db, id, status)
        send_video_processing_result(self.request.id, status)
        if tdir is not None:
            shutil.rmtree(tdir)
        raise

@app.task(base=DatabaseTask, ignore_result=True, priority=5)
def create_dash(id):
    db = create_dash.db
    tdir = None
    try:
        eReq = crud.get_video_encoding_request_by_id(db, id)
        tdir = eReq.tdir
        input = os.path.join(tdir, ORIGINAL_FILE_NAME)
        
        # create 360p encoded video
        cmd = get_ffmpeg_cmd(input, tdir, 1)
        subprocess.check_call(cmd, shell=True)

        # create MPEG-DASH
        subprocess.check_call(get_dash_cmd(input, eReq, [0,1]), shell=True)
        
        # upload folder to s3 using aws sync
        subprocess.check_call(get_aws_sync_command(eReq), shell=True)                      
        crud.update_vp_request_status(db, eReq, VideoEncodingStatus.SUCCESS)
    except Exception as e:
        print(f"error processing request {id} err={e}")
        crud.update_ve_request_by_id(db, id, VideoEncodingStatus.FAILED)
        return False
    # finally:
    #     if tdir is not None:
    #         shutil.rmtree(tdir)
    return True


def get_ffmpeg_cmd(input, outputDir, otherParamIndex):
    op = otherParams[otherParamIndex]
    output = os.path.join(outputDir, f'{op["name"]}.mp4')
    return f"""ffmpeg -i {input} -c:a aac -vf scale={op["video_width"]}:-2 
          -c:v libx264 -x264-params scenecut=0:open_gop=0:min-keyint=72:keyint=72 
          -minrate {op["kbPerSec"]} -maxrate {op['kbPerSec']} 
           -bufsize {op['kbPerSec']} -b:v {op['kbPerSec']} -preset ultrafast -y {output}""".replace("\n",'') 


def get_dash_cmd(original: str, req: models.VideoEncodingRequest, pi):
    cmd = "packager "
    if req.has_audio:
        cmd += (f"in='{original}',stream=audio,"
               f"""init_segment='{os.path.join(req.toutdir, 'audio/init.mp4')}',"""
               f"segment_template='{os.path.join(req.toutdir, 'audio/$Number$.m4s')}' ")

    for i in pi:
        p = otherParams[i]
        cmd += (f"""in='{os.path.join(req.tdir, f'{p["name"]}.mp4')}',stream=video,"""
                f"""init_segment='{os.path.join(req.toutdir, f'{p["name"]}/init.mp4')}',"""
                f"""segment_template='{os.path.join(req.toutdir, f'{p["name"]}/$Number$.m4s')}' """)

    cmd += ("--generate_static_live_mpd --segment_duration 3 --mpd_output "
            f"{os.path.join(req.toutdir, DASH_MPD_FILE_NAME)} --base_urls {req.base_url}")
    return cmd 


def create_video_thumbnail(tdir):
    input = os.path.join(tdir,f"{otherParams[0]['name']}.mp4")
    output = os.path.join(tdir, VIDEO_THUMBNAIL_FILE_NAME)
    cmd = (f"ffmpeg -ss 00:00:01.000 -i {input} -vframes 1 -q:v 2 {output}")
    subprocess.check_call(cmd, shell=True)
    return output


def get_aws_sync_command(req: models.VideoEncodingRequest):
    return (f"AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID} " 
            f"AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY} aws s3 sync " 
            f"{req.toutdir} s3://{S3_OUTPUT_BUCKET}/{req.object_key}")


def send_video_processing_result(taskId: str, status: models.VideoEncodingStatus):
    url = f'{MAIN_API_ENDPOINT}/video/processing/result'
    headers = {'ApiKey': MAIN_API_KEY}
    r = requests.put(url, json = {'taskId': taskId, 'status': status.name}, headers=headers)
    print("send_video_processing_result", r)
    