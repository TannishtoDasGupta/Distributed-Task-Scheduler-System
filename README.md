# Distributed Task Scheduler System

A containerised backend starter for submitting, processing, and monitoring asynchronous tasks with **FastAPI**, **Celery**, **Redis**, and **PostgreSQL**.

> **Project status:** early-stage project. The built-in task handlers currently support `echo`, `sum`, and `concat`. This is a learning and extension-friendly foundation, not a production-hardened scheduling platform.

## Architecture

- **FastAPI** exposes the task submission and status APIs.
- **PostgreSQL** stores task metadata, payloads, results, and retry counts.
- **Redis** acts as the Celery message broker and result backend.
- **Celery worker** executes registered task handlers asynchronously.
- **Docker Compose** starts the API, worker, database, and broker.

```text
Client
  |
  v
FastAPI -----> PostgreSQL
  |
  v
Redis broker ---> Celery worker
                       |
                       v
                  Task handler
                       |
                       v
                  PostgreSQL
```

## Requirements

- Docker Engine
- Docker Compose plugin

## Quick start (Docker)

1. Clone the repository:

   ```bash
   git clone https://github.com/TannishtoDasGupta/Distributed-Task-Scheduler-System.git
   cd Distributed-Task-Scheduler-System
   ```

2. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

   Change the example database password even for shared development environments. The Compose ports are bound to `127.0.0.1` for local use; do not expose the API publicly without authentication and authorisation. Do not commit `.env`.

3. Build and start the services:

   ```bash
   docker compose up --build
   ```

4. Open the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs). The liveness endpoint is [http://localhost:8000/health](http://localhost:8000/health); the readiness endpoint is [http://localhost:8000/ready](http://localhost:8000/ready) and checks PostgreSQL connectivity.

Stop the services with `docker compose down`. To also delete the local PostgreSQL volume, use `docker compose down -v` (this permanently deletes its stored data).

## API

### Submit a task

`POST /api/tasks/`

Example: echo a JSON payload.

```json
{
  "type": "echo",
  "payload": {
    "message": "hello"
  }
}
```

Example: add numbers.

```json
{
  "type": "sum",
  "payload": {
    "values": [10, 20, 30]
  }
}
```

Example: concatenate strings.

```json
{
  "type": "concat",
  "payload": {
    "values": ["distributed", "-", "tasks"]
  }
}
```

The API returns HTTP `202 Accepted` and a task ID. Processing happens asynchronously; poll the status endpoint to see the current state. If the broker is unavailable, the API returns HTTP `503` and marks the persisted task as `FAILED`.

### Get a task

`GET /api/tasks/{task_id}`

### List recent tasks

`GET /api/tasks/`

The list endpoint returns at most the 100 most recently created tasks.

### Task states

- `PENDING`: accepted and waiting for a worker.
- `PROCESSING`: a worker is executing the task.
- `RETRY`: a retry has been scheduled after a processing error.
- `SUCCESS`: completed successfully.
- `FAILED`: execution failed permanently.

## Run tests locally

Create and activate a virtual environment, install dependencies, then run the unit tests:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The unit tests cover task handlers and request-schema validation; they do not require a running database or Redis instance.

## Configuration

Copy `.env.example` to `.env`. The settings cover PostgreSQL connection details, Redis/Celery URLs, and the maximum number of task retries. Environment variables supplied by the deployment environment take precedence over the file.

## Extending the system

Add new task types in `app/workers/handlers.py` and cover them with unit tests in `tests/`. Keep task handlers deterministic where possible, validate their input, and avoid placing secrets or sensitive data in task payloads.

## Security and limitations

- The API currently has no authentication or authorisation. Compose binds published ports to localhost, but this is not an access-control layer; do not expose the API publicly without adding authentication and authorisation.
- Use strong, unique database credentials outside local development.
- Restrict network access to PostgreSQL and Redis in production.
- The starter creates tables at application startup. Add and run Alembic migrations before evolving the database schema in deployed environments.
- Task payloads and results are stored in PostgreSQL; do not submit credentials, patient data, or other sensitive information.
- Delivery guarantees, idempotency, rate limiting, observability, and production deployment hardening require further work.

## Contributing

Bug reports, documentation improvements, tests, and focused pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Maintainer

Created and maintained by [TannishtoDasGupta](https://github.com/TannishtoDasGupta).
