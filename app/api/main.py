from debugger import initialize_fast_api_server_debugger_if_needed

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from celery.result import AsyncResult

from . import payload,deps

from sqlalchemy.orm import Session
from db import crud, models
from db.database import engine

from worker.tasks import create_initial_dash, create_dash

models.Base.metadata.create_all(bind=engine)

initialize_fast_api_server_debugger_if_needed()

app = FastAPI()

@app.post("/video/encoding")
def create_ve_request(req: payload.CreateVERequest, 
                    _: APIKey = Depends(deps.get_api_key), 
                    db: Session = Depends(deps.get_db)):
    res = crud.create_video_encoding_request(db, req)
    task = create_initial_dash.apply_async((res.id,), link=create_dash.s())
    return JSONResponse(content=task.task_id) 

@app.get("/video/encoding/{task_id}")
def get_status(task_id, 
               _: APIKey = Depends(deps.get_api_key)):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)    