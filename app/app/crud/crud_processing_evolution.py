from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import ProcessingEvolutionRequest
from app.schemas.processing_evolution import CreateProcessingEvolution, UpdateProcessingEvolution, ProcessingStatus


class CRUD(CRUDBase[ProcessingEvolutionRequest, CreateProcessingEvolution, UpdateProcessingEvolution]):
    def set_failed(self, db: Session, id: int, error_msg: str = None):
        req = self.get(db, id = id)
        req.status = ProcessingStatus.failed.value
        if error_msg:
            req.error_msg = error_msg
        db.add(req)
        db.commit()

    def set_success(self, db: Session, id: int, img_base64: str, imagepath: str, result: dict):
        req = self.get(db, id = id)
        req.status = ProcessingStatus.done.value
        req.result = result
        req.imagepath = imagepath
        req.image_base64 = img_base64
        db.add(req)
        db.commit()
            
evolution_req = CRUD(ProcessingEvolutionRequest)
