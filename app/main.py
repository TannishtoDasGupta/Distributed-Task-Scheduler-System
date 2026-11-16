from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from .database import engine
from .routes import task_routes
from .utils.logger import logger

app = FastAPI(
    title="Distributed Task Scheduler",
    description="Submit, execute, and monitor asynchronous tasks. Task endpoints require an API key.",
    version="0.2.0",
)
app.include_router(task_routes.router, prefix="/api/tasks", tags=["tasks"])


@app.on_event("startup")
def startup_event():
    # Database schema is managed explicitly through Alembic migrations.
    logger.info("Application startup completed")


@app.get("/health", tags=["health"])
def health():
    """Liveness check: confirms that the API process is responding."""
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
def readiness():
    """Readiness check: confirms that PostgreSQL is reachable."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        logger.exception("Readiness check failed: database unavailable")
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready"}
