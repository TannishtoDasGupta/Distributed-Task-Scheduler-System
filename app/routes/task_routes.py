import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Task
from ..schemas import TaskCreate, TaskOut
from ..security import require_api_key
from ..utils.logger import logger
from ..workers.tasks import enqueue_task

router = APIRouter(dependencies=[Depends(require_api_key)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TaskOut, status_code=status.HTTP_202_ACCEPTED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task_uuid = str(uuid.uuid4())
    task_payload = payload.payload
    db_task = Task(task_id=task_uuid, type=payload.type, status="PENDING", payload=json.dumps(task_payload))
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    try:
        enqueue_task.apply_async(args=[db_task.task_id, payload.type, task_payload])
    except Exception as exc:
        db_task.status = "FAILED"
        db_task.result = json.dumps({"error": "Task broker is unavailable"})
        db.commit()
        logger.exception("Could not enqueue task %s", db_task.task_id)
        raise HTTPException(status_code=503, detail="Task queue is temporarily unavailable") from exc
    logger.info("Enqueued task %s of type %s", db_task.task_id, db_task.type)
    return TaskOut(task_id=db_task.task_id, type=db_task.type, status=db_task.status, retries=db_task.retries, payload=task_payload, result=None)

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: str, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut(task_id=db_task.task_id, type=db_task.type, status=db_task.status, retries=db_task.retries, payload=json.loads(db_task.payload) if db_task.payload is not None else None, result=json.loads(db_task.result) if db_task.result is not None else None)

@router.get("/", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(100).all()
    return [TaskOut(task_id=t.task_id, type=t.type, status=t.status, retries=t.retries, payload=json.loads(t.payload) if t.payload is not None else None, result=json.loads(t.result) if t.result is not None else None) for t in tasks]
