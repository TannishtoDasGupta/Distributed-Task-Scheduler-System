from fastapi import FastAPI
from sqlalchemy import text

from .database import Base, engine
from .routes import task_routes
from .utils.logger import logger

app = FastAPI(
    title="Distributed Task Scheduler",
    description="Submit, execute, and monitor asynchronous tasks.",
    version="0.1.0",
)
app.include_router(task_routes.router, prefix="/api/tasks", tags=["tasks"])


@app.on_event("startup")
def startup_event():
    # Compose waits for PostgreSQL to become healthy before starting the API.
    # create_all is suitable for this starter; use Alembic migrations for
    # controlled schema changes in deployed environments.
    Base.metadata.create_all(bind=engine)
    logger.info("Application startup completed")


@app.get("/health", tags=["health"])
def health():
    """Liveness check: confirms that the API process is responding."""
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
def readiness():
    """Readiness check: confirms PostgreSQL is reachable."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Readiness check failed: database unavailable")
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ready"}
