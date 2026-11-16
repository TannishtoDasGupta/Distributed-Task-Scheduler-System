"""End-to-end task execution against real Redis, Celery worker, and PostgreSQL.

The CI workflow starts the broker and worker. Set RUN_CELERY_INTEGRATION=1
to enable this test locally when those services are available.
"""
import json
import os
import time
import uuid

import pytest

from app.database import SessionLocal
from app.models import Task
from app.workers.tasks import enqueue_task


@pytest.mark.skipif(
    os.getenv("RUN_CELERY_INTEGRATION") != "1",
    reason="requires a running Redis broker, Celery worker, and PostgreSQL",
)
def test_task_is_executed_by_worker_and_persisted():
    task_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        db.add(
            Task(
                task_id=task_id,
                type="sum",
                status="PENDING",
                payload=json.dumps({"values": [2, 3, 5]}),
            )
        )
        db.commit()
    finally:
        db.close()

    try:
        async_result = enqueue_task.apply_async(
            args=[task_id, "sum", {"values": [2, 3, 5]}]
        )
        deadline = time.monotonic() + 30
        observed_status = None
        observed_result = None

        while time.monotonic() < deadline:
            db = SessionLocal()
            try:
                stored = db.query(Task).filter(Task.task_id == task_id).one()
                observed_status = stored.status
                observed_result = (
                    json.loads(stored.result) if stored.result is not None else None
                )
            finally:
                db.close()

            if observed_status in {"SUCCESS", "FAILED"}:
                break
            time.sleep(0.25)

        assert observed_status == "SUCCESS", (
            f"worker did not complete task; status={observed_status!r}; "
            f"celery_result={async_result.status!r}"
        )
        assert observed_result == {"sum": 10}
        assert async_result.get(timeout=5) == {"sum": 10}
    finally:
        db = SessionLocal()
        try:
            db.query(Task).filter(Task.task_id == task_id).delete()
            db.commit()
        finally:
            db.close()
