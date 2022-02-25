import os

from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

from starlette.status import HTTP_403_FORBIDDEN

from db.database import SessionLocal


# Databse Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

APP_API_KEY = os.environ.get("APP_API_KEY")
API_KEY_NAME = "ApiKey"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == APP_API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")