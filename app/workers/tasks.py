"""Celery tasks that execute work and persist task lifecycle updates."""
import json

from ..database import SessionLocal
from ..models import Task
from ..utils.logger import logger
from .celery_worker import celery_app
from .handlers import execute_task


@celery_app.task(bind=True, name="app.workers.tasks.enqueue_task")
def enqueue_task(self, task_id: str, task_type: str, payload: dict):
    """Execute a task, persist its state, and retry transient failures."""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task is None:
            logger.warning("Task %s was not found; skipping execution", task_id)
            return None

        task.status = "PROCESSING"
        task.retries = self.request.retries
        db.commit()

        try:
            result = execute_task(task_type, payload or {})
        except ValueError as exc:
            # Invalid input and unsupported task types are permanent failures.
            task.status = "FAILED"
            task.result = json.dumps({"error": str(exc)})
            task.retries = self.request.retries
            db.commit()
            logger.warning("Task %s failed validation: %s", task_id, exc)
            return {"status": "FAILED", "error": str(exc)}
        except Exception as exc:
            db.rollback()
            task = db.query(Task).filter(Task.task_id == task_id).first()
            if task is None:
                raise

            next_retry = self.request.retries + 1
            task.retries = next_retry
            if self.request.retries < task_max_retries():
                task.status = "RETRY"
                db.commit()
                logger.exception("Task %s failed; scheduling retry %s", task_id, next_retry)
                raise self.retry(
                    exc=exc,
                    countdown=min(2 ** next_retry, 60),
                    max_retries=task_max_retries(),
                )

            task.status = "FAILED"
            task.result = json.dumps({"error": str(exc)})
            db.commit()
            logger.exception("Task %s exhausted retries", task_id)
            raise

        task.status = "SUCCESS"
        task.result = json.dumps(result)
        task.retries = self.request.retries
        db.commit()
        logger.info("Task %s completed successfully", task_id)
        return result
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def task_max_retries() -> int:
    """Read the configured retry count without duplicating configuration."""
    from ..config import settings

    return settings.task_max_retries
