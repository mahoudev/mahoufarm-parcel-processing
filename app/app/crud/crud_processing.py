from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import ProcessingRequest
from app.schemas.processing_request import CreateProcessingRequest, UpdateProcessingRequest, ProcessingStatus


class CRUD(CRUDBase[ProcessingRequest, CreateProcessingRequest, UpdateProcessingRequest]):
    def set_failed(self, db: Session, id: int, error_msg: str = None):
        req = self.get(db, id = id)
        req.status = ProcessingStatus.failed
        if error_msg:
            req.error_msg = error_msg
        db.add(req)
        db.commit()

    def set_success(self, db: Session, id: int, imagepath: str, result: dict):
        req = self.get(db, id = id)
        req.status = ProcessingStatus.done.value
        req.result = result
        req.imagepath = imagepath
        db.add(req)
        db.commit()
            
processing_req = CRUD(ProcessingRequest)
