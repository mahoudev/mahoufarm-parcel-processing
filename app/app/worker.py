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
import requests


from app.utils import pipeline_ndvi, pipeline_ndmi
from app import schemas, crud
from app.config import settings
from app.db.session import SessionLocal

def notify_failed(internal_proc_id: int, external_proc_id: int, webhook_url: str, exception = None):
    print("Will notify failure to ", webhook_url)
    res = requests.post(
        url = webhook_url,
        data = json.dumps({
            'status': schemas.processing_request.ProcessingStatus.failed.value,
            'external_id': external_proc_id,
            'id': internal_proc_id,
            'reason': str(exception)
        }),
        headers= {
            'Content-Type': 'application/json'
        }
    )
    print(res.text, res)

def notify_success(
    internal_proc_id: int, 
    external_proc_id: int, 
    webhook_url: str, 
    img_base64: str
    
):
    print("Will notify success to ", webhook_url)
    res = requests.post(
        url = webhook_url,
        data = json.dumps({
            'status': schemas.processing_request.ProcessingStatus.done.value,
            'external_id': external_proc_id,
            'id': internal_proc_id,
            'image_base64': str(img_base64)
        }),
        headers= {
            'Content-Type': 'application/json'
        }
    )

    print(res.text, res)


@celery_app.task(name="process_ndvi")
def process_ndvi(internal_proc_id: int, external_proc_id: int, webhook_url: str, polygon_coordinates: list[list]):
    try:
        res = pipeline_ndvi(polygone=polygon_coordinates)
        print("OUTPUT NDVI ", res, type(res))
        print("/////////// ", res.model_dump())
        print("/////////// ", res.model_dump_json())
        
    except Exception as e:
        db = SessionLocal()
        crud.processing_req.set_failed(db, internal_proc_id, error_msg=str(e))
        db.close()
        
        notify_failed(internal_proc_id, external_proc_id, webhook_url, exception = e)
    else:
        result_dict = res.model_dump()
        del result_dict['image_base64']

        db = SessionLocal()
        crud.processing_req.set_success(
            db, 
            internal_proc_id, 
            img_base64 = res.image_base64, 
            imagepath = os.path.basename(res.path), 
            result= result_dict
        )
        db.close()

        notify_success(
            internal_proc_id, 
            external_proc_id, 
            webhook_url, 
            img_base64=res.image_base64
        )


@celery_app.task(name="process_nmvi")
def process_ndmi(internal_proc_id: int, external_proc_id: int, webhook_url: str, polygon_coordinates: list[list]):
    try:
        res = pipeline_ndmi(polygone=polygon_coordinates)
        print("OUTPUT NDMI ##############", res, res)
        print("/////////// ", res.model_dump())
        print("/////////// ", res.model_dump_json())

    except Exception as e:
        db = SessionLocal()
        crud.processing_req.set_failed(db, internal_proc_id, error_msg=str(e))
        db.close()
        
        notify_failed(internal_proc_id, external_proc_id, webhook_url, exception = e)
    else:
        result_dict = res.model_dump()
        del result_dict['image_base64']
        
        db = SessionLocal()
        crud.processing_req.set_success(
            db, 
            internal_proc_id, 
            img_base64 = res.image_base64, 
            imagepath = os.path.basename(res.path), 
            result= result_dict
        )
        db.close()

        notify_success(
            internal_proc_id, 
            external_proc_id, 
            webhook_url, 
            img_base64=res.image_base64
        )
