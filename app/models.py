from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, index=True, nullable=False)
    idempotency_key = Column(String(128), unique=True, index=True, nullable=True)
    request_hash = Column(String(64), nullable=True)
    type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    payload = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    retries = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
