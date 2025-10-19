from fastapi import FastAPI
from .routes import task_routes
from .database import engine, Base
from .utils.logger import logger

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Distributed Task Scheduler")
app.include_router(task_routes.router, prefix="/api/tasks", tags=["tasks"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")

@app.get("/health")
async def health():
    return {"status": "ok"}