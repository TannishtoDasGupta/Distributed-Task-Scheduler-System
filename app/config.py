from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_key: str | None = Field(default=None, min_length=32)
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_port: int = 5432
    redis_host: str = "redis"
    redis_port: int = 6379
    celery_broker_url: str
    celery_result_backend: str
    task_max_retries: int = 3
    class Config:
        env_file = ".env"

settings = Settings()
