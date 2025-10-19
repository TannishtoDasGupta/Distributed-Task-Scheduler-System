from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid, json
from ..schemas import TaskCreate, TaskOut
from ..database import SessionLocal
from ..models import Task
from ..utils.logger import logger
from ..workers.tasks import enqueue_task

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TaskOut)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task_uuid = str(uuid.uuid4())
    db_task = Task(task_id=task_uuid, type=payload.type, status="PENDING",
                   payload=json.dumps(payload.payload) if payload.payload else None)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    enqueue_task.apply_async(args=[db_task.task_id, payload.type, payload.payload or {}])
    logger.info(f"Enqueued task {db_task.task_id} of type {db_task.type}")
    return TaskOut(task_id=db_task.task_id, type=db_task.type, status=db_task.status,
                   retries=db_task.retries, payload=payload.payload, result=None)

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: str, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    payload = json.loads(db_task.payload) if db_task.payload else None
    result = json.loads(db_task.result) if db_task.result else None
    return TaskOut(task_id=db_task.task_id, type=db_task.type, status=db_task.status,
                   retries=db_task.retries, payload=payload, result=result)

@router.get("/")
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(100).all()
    return [TaskOut(task_id=t.task_id, type=t.type, status=t.status,
                    retries=t.retries, payload=(json.loads(t.payload) if t.payload else None),
                    result=(json.loads(t.result) if t.result else None)) for t in tasks]