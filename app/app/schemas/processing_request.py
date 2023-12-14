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
    matrix: list[list] = []

class CreateProcessingRequest(BaseProcessingRequest):
    id_initiator: int
    polygon_coordinates: list[list]
    process_type: ProcessingType
    status: ProcessingStatus
    task_id: str

class UpdateProcessingRequest(BaseModel):
    status: Optional[ProcessingStatus]
    error_msg: Optional[str]
    matrix: Optional[list[list]]
    result: Optional[dict]
    
class APICreateProcessingRequest(CreateProcessingRequest):
    pass

class APIInputNDVI(BaseModel):
    polygon_coordinates: list[list]
    
class NDVIOutput(BaseModel):
  path: str
  value: float
  image_base64: Optional[str]
  polygon_area: Optional[float]

class ProcessingOutput(BaseModel):
  matrix: list
  mean_value: float
  image_base64: Optional[str]
  polygon_area: Optional[float]
  used_tile_name: str