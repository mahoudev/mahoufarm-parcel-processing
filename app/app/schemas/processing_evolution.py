from pydantic import BaseModel
import enum
from typing import Any, Optional

class ProcessingStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"

class ProcessingType(enum.Enum):
    ndvi = "ndvi"
    ndmi = "ndmi"
    ndvi_evolution = "ndvi_evolution"

class BaseProcessingEvolution(BaseModel):
    id_initiator: Optional[int]
    image1: Optional[str]
    image2: Optional[str]
    process_type: Optional[ProcessingType]
    status: Optional[ProcessingStatus]
    task_id: Optional[str]
    error_msg: Optional[str]
    result: Optional[dict]
    imagepath: Optional[str]

class CreateProcessingEvolution(BaseProcessingEvolution):
    id_initiator: int
    image1: str
    image2: str
    process_type: ProcessingType
    status: ProcessingStatus
    task_id: str

class UpdateProcessingEvolution(BaseModel):
    status: Optional[ProcessingStatus]
    error_msg: Optional[str]

class APICreateProcessingEvolution(CreateProcessingEvolution):
    pass

class APIInput(BaseModel):
    polygon_coordinates: list[list]
    
class EvolutionOutput(BaseModel):
  image_base64: str
