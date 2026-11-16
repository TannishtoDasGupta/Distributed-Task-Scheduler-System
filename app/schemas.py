from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, constr


class TaskCreate(BaseModel):
    type: constr(strip_whitespace=True, min_length=1, max_length=50)
    payload: Dict[str, Any] = Field(default_factory=dict)


class TaskOut(BaseModel):
    task_id: str
    type: str
    status: str
    retries: int
    payload: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
