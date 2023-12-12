from typing import Any
import datetime 
from sqlalchemy import create_engine, Column, Text, Integer, JSON, String
from sqlalchemy.orm import Mapped

from app import schemas
from app.db.base import Base

class ProcessingRequest(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    id_initiator: Mapped[int] = Column(Integer, nullable=False)
    polygon_coordinates: Mapped[list] = Column(JSON, default=[])
    process_type: Mapped[schemas.processing_request.ProcessingType] = Column(String, nullable=False)
    status: Mapped[str] = Column(String, default=schemas.processing_request.ProcessingStatus.pending)
    task_id: Mapped[str] = Column(String)
    error_msg: Mapped[str] = Column(Text)
    result: Mapped[dict] = Column(JSON)
    imagepath: Mapped[str] = Column(String)
    image_base64: Mapped[str] = Column(Text)