from celery import Celery
import os

# celery_app = Celery(__name__, backend="redis://redis/0", broker="redis://redis/0")

from dotenv import load_dotenv

load_dotenv(".env")

celery_app = Celery(__name__)
celery_app.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery_app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")

print("\n\n\n CELERY AT ", os.environ.get("CELERY_BROKER_URL"), os.environ.get("CELERY_RESULT_BACKEND"))


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"

from fastapi import FastAPI, Depends, HTTPException, status
from celery.result import AsyncResult
from pydantic import BaseModel
from celery.states import SUCCESS
from typing import Optional
import time, json, requests

from app.utils import pipeline_ndvi
from app import schemas, crud
from app.db.session import SessionLocal

def notify_failed(process_id: int, exception = None):
    db = SessionLocal()
    crud.processing_req.set_failed(db, process_id, error_msg=str(exception))
    db.close()

def notify_success(process_id: int, result: schemas.processing_request.NDVIOutput):
    db = SessionLocal()
    crud.processing_req.set_success(db, process_id, imagepath = result.path, result= result.model_dump())
    db.close()

@celery_app.task(name="process_ndvi")
def process_ndvi(process_id: int, polygon_coordinates: list[list]):
    try:
        res = pipeline_ndvi(polygone=polygon_coordinates)
    except Exception as e:
        notify_failed(process_id, exception = e)
    else:
        notify_success(process_id, result = res)