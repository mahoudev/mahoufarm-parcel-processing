from typing import Generator

from fastapi import FastAPI, Body, Request, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
import uuid

from app.worker import process_ndvi, process_ndmi, process_evolution_ndvi
from app import models, schemas, crud, utils
from app.config import settings
from app.db.session import SessionLocal, get_db

router = APIRouter()

poly = [
            [
              -4.0701520094588375,
              5.4326077982032785
            ],
            [
              -4.092201908402217,
              5.410244948985962
            ],
            [
              -4.069462950117014,
              5.380746675499253
            ],
            [
              -4.0388687153344165,
              5.372925962777828
            ],
            [
              -4.006758549997869,
              5.410519344789904
            ],
            [
              -4.047688674911484,
              5.427668835319736
            ],
            [
              -4.0701520094588375,
              5.4326077982032785
            ]
          ]

# utils.pipeline_ndmi(poly)
# utils.pipeline_ndvi(poly)
@router.post("/process/ndvi")
def create_process_ndvi(
    request: Request,
    db: Session = Depends(get_db),
    polygon_coordinates: list[list] = Body(...), # [[lat, lon], [lat, lon], ...]
    id_user: int = Body(...),
    request_identifier: int = Body(...),
    webhook: str = Body(...),
):
    if request.headers.get("Authorization") != settings.AUTH_KEY:
        raise HTTPException(status_code=401, detail="Not authenticated")
    proc = models.ProcessingRequest(
        id_initiator = id_user,
        process_type = schemas.processing_request.ProcessingType.ndvi.value,
        polygon_coordinates = polygon_coordinates,
        status = schemas.processing_request.ProcessingStatus.pending.value
    )

    db.add(proc)
    db.commit()

    task = process_ndvi.delay(proc.id, request_identifier, webhook, polygon_coordinates)

    proc.task_id = task.task_id
    db.add(proc)
    db.commit()

    return JSONResponse({"id": proc.id})

@router.post("/process/ndmi")
def create_process_ndmi(
    request: Request,
    db: Session = Depends(get_db),
    polygon_coordinates: list[list] = Body(...), # [[lat, lon], [lat, lon], ...]
    id_user: int = Body(...),
    request_identifier: int = Body(...),
    webhook: str = Body(...),
):
    if request.headers.get("Authorization") != settings.AUTH_KEY:
        raise HTTPException(status_code=401, detail="Not authenticated")
    proc = models.ProcessingRequest(
        id_initiator = id_user,
        process_type = schemas.processing_request.ProcessingType.ndmi.value,
        polygon_coordinates = polygon_coordinates,
        status = schemas.processing_request.ProcessingStatus.pending.value
    )

    db.add(proc)
    db.commit()

    task = process_ndmi.delay(proc.id, request_identifier, webhook, polygon_coordinates)

    proc.task_id = task.task_id
    db.add(proc)
    db.commit()

    return JSONResponse({"id": proc.id})


@router.post("/process-evolution/{process_type}")
def create_process_evolution_ndvi(
    request: Request,
    process_type: schemas.processing_request.ProcessingType,
    db: Session = Depends(get_db),
    id_user: int = Body(...),
    request_identifier: int = Body(...),
    image1: str = Body(...),
    image2: str = Body(...),
    webhook: str = Body(...),
):
    if request.headers.get("Authorization") != settings.AUTH_KEY:
        raise HTTPException(status_code=401, detail="Not authenticated")
    proc = models.ProcessingEvolutionRequest(
        id_initiator = id_user,
        process_type = process_type.value,
        image1 = image1,
        image2 = image2,
        status = schemas.processing_request.ProcessingStatus.pending.value
    )

    db.add(proc)
    db.commit()

    task = process_evolution_ndvi.delay(
        internal_proc_id = proc.id, 
        external_proc_id = request_identifier, 
        webhook_url = webhook, 
        first_ndvi_base64 = image1,
        second_ndvi_base64 = image2
    )

    proc.task_id = task.task_id
    db.add(proc)
    db.commit()

    return JSONResponse({"id": proc.id})

@router.get("/process/{req_id}")
def read_process(
    request: Request,
    req_id: int,
    db: Session = Depends(get_db)
):
    # if request.headers.get("Authorization") != settings.AUTH_KEY:
    #     raise HTTPException(status_code=401, detail="Not authenticated")
    
    req = crud.processing_req.get(db, id=req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request ID does not exist")
    return req

@router.get("/process-evolution/{req_id}")
def read_process(
    request: Request,
    req_id: int,
    db: Session = Depends(get_db)
):
    # if request.headers.get("Authorization") != settings.AUTH_KEY:
    #     raise HTTPException(status_code=401, detail="Not authenticated")
    
    req = db.query(models.ProcessingEvolutionRequest).get(req_id)
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