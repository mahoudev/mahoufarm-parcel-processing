from typing import Generator

from fastapi import FastAPI, Body, Request, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
import uuid

from app.worker import process_ndvi
from app import models, schemas, crud
from app.config import settings
from app.db.session import SessionLocal, get_db


router = APIRouter()

@router.post("/process/ndvi")
def create_process(
    request: Request,
    db: Session = Depends(get_db),
    polygon_coordinates: list[list] = Body(...), # [[lat, lon], [lat, lon], ...]
    id_user: int = Body(...),
    webhook: str = Body(...),
):
    if request.headers.get("Authorization") != settings.AUTH_KEY:
        raise HTTPException(status_code=401, detail="Not authenticated")
    proc = models.ProcessingRequest(
        id_initiator = id_user,
        polygon_coordinates = polygon_coordinates,
        process_type = schemas.processing_request.ProcessingType.ndvi.value,
        status = schemas.processing_request.ProcessingStatus.pending.value
    )

    db.add(proc)
    db.commit()

    task = process_ndvi.delay(proc.id, polygon_coordinates)

    proc.task_id = task.task_id
    db.add(proc)
    db.commit()

    return JSONResponse({"id": proc.id})

@router.get("/process/ndvi/{req_id}")
def read_root(
    request: Request,
    req_id: int,
    db: Session = Depends(get_db)
):
    if request.headers.get("Authorization") != settings.AUTH_KEY:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    req = crud.processing_req.get(db, id=req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request ID does not exist")
    return req

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.PREFIX_ENDPOINT)
app.mount(settings.STATICFILES_ENDPOINT, StaticFiles(directory = settings.STATICFILES_DIR), name="static")