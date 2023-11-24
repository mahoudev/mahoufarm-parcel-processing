from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from typing import Any, Generator
import datetime 
from sqlalchemy import create_engine, Column, DateTime, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, Session, declared_attr

class Base(DeclarativeBase):
    id: Any
    created_at = Column(DateTime, default = datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate = datetime.datetime.utcnow, default = datetime.datetime.utcnow)
    
    __name__: str
    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI.unicode_string(), echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=True)

def get_db(val = "DEFAULT ") -> Generator:
    try:
        print("\n TRYING GET DB -- ", val)
        db: Session =  SessionLocal()
        yield db
    except:
        print("CLOSE DB -- ", val)
        db.close()