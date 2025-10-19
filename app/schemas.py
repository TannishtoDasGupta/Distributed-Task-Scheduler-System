from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    type: str
    payload: Optional[dict] = None

class TaskOut(BaseModel):
    task_id: str
    type: str
    status: str
    retries: int
    payload: Optional[dict] = None
    result: Optional[dict] = None

    class Config:
        orm_mode = True