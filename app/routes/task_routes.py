import hashlib
import json
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
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


def request_fingerprint(task_type: str, payload: dict) -> str:
    """Stable hash used to reject reuse of an idempotency key for new input."""
    canonical = json.dumps(
        {"type": task_type, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def serialize_task(task: Task) -> TaskOut:
    return TaskOut(
        task_id=task.task_id,
        type=task.type,
        status=task.status,
        retries=task.retries,
        payload=json.loads(task.payload) if task.payload is not None else None,
        result=json.loads(task.result) if task.result is not None else None,
    )


def resolve_idempotent_replay(task: Task, fingerprint: str) -> TaskOut:
    if task.request_hash != fingerprint:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency-Key was already used with a different request",
        )
    return serialize_task(task)


@router.post("/", response_model=TaskOut, status_code=status.HTTP_202_ACCEPTED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if idempotency_key is not None:
        idempotency_key = idempotency_key.strip()
        if not idempotency_key or len(idempotency_key) > 128:
            raise HTTPException(status_code=400, detail="Idempotency-Key must contain 1-128 characters")

    task_payload = payload.payload
    fingerprint = request_fingerprint(payload.type, task_payload)
    if idempotency_key:
        existing = db.query(Task).filter(Task.idempotency_key == idempotency_key).first()
        if existing:
            return resolve_idempotent_replay(existing, fingerprint)

    db_task = Task(
        task_id=str(uuid.uuid4()),
        idempotency_key=idempotency_key,
        request_hash=fingerprint if idempotency_key else None,
        type=payload.type,
        status="PENDING",
        payload=json.dumps(task_payload),
    )
    db.add(db_task)
    try:
        db.commit()
    except IntegrityError:
        # A concurrent request may have committed this key after our first lookup.
        db.rollback()
        if idempotency_key:
            existing = db.query(Task).filter(Task.idempotency_key == idempotency_key).first()
            if existing:
                return resolve_idempotent_replay(existing, fingerprint)
        raise
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
    return serialize_task(db_task)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: str, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize_task(db_task)


@router.get("/", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(100).all()
    return [serialize_task(task) for task in tasks]
