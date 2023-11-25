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

class BaseProcessingRequest(BaseModel):
    id_initiator: Optional[int]
    polygon_coordinates: list[list]
    process_type: Optional[ProcessingType]
    status: Optional[ProcessingStatus]
    task_id: Optional[str]
    error_msg: Optional[str]
    result: Optional[dict]
    imagepath: Optional[str]

class CreateProcessingRequest(BaseProcessingRequest):
    id_initiator: int
    polygon_coordinates: list[list]
    process_type: ProcessingType
    status: ProcessingStatus
    task_id: str

class UpdateProcessingRequest(BaseModel):
    status: Optional[ProcessingStatus]
    error_msg: Optional[str]

class APICreateProcessingRequest(CreateProcessingRequest):
    pass

class APIInputNDVI(BaseModel):
    polygon_coordinates: list[list]
    
class NDVIOutput(BaseModel):
  path: str
  value: float
  polygon_area: float