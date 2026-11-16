# Distributed Task Scheduler System

A containerised backend starter for submitting, processing, and monitoring asynchronous tasks with **FastAPI**, **Celery**, **Redis**, and **PostgreSQL**.

> **Project status:** early-stage project. Built-in handlers support `echo`, `sum`, and `concat`. This repository provides a deployable API/worker stack, not a hosted public website or a production-certified scheduling platform.

## Architecture

- **FastAPI** exposes authenticated task submission and status APIs.
- **PostgreSQL** stores task metadata, payloads, results, idempotency keys, and retry counts.
- **Redis** acts as the Celery message broker and result backend.
- **Celery worker** executes registered task handlers asynchronously.
- **Alembic** manages versioned database schema migrations.
- **Docker Compose** starts the API, worker, database, and broker.

## Requirements

- Python 3.11+
- Docker Engine and Docker Compose plugin

## Quick start

```bash
git clone https://github.com/TannishtoDasGupta/Distributed-Task-Scheduler-System.git
cd Distributed-Task-Scheduler-System
cp .env.example .env
```

Generate strong secrets (at least 32 characters) and set `API_KEY` and `POSTGRES_PASSWORD` in `.env`. Never commit the real `.env` file.

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
docker compose up --build
```

Open [http://localhost:8000/docs](http://localhost:8000/docs). In Swagger, click **Authorize** and enter your secret as `X-API-Key`. The API, PostgreSQL, and Redis host ports are bound to localhost only. Stop with `docker compose down`; `docker compose down -v` also deletes the local database volume.

## API

All `/api/tasks` endpoints require the `X-API-Key` header.

### Submit a task

`POST /api/tasks/` returns HTTP `202 Accepted`.

```http
X-API-Key: your-generated-secret
Idempotency-Key: unique-request-123
Content-Type: application/json
```

```json
{"type":"sum","payload":{"values":[2,3,5]}}
```

The optional `Idempotency-Key` (1-128 characters) makes client retries safe: repeating the same key and identical request returns the original task. Reusing the key with different input returns HTTP `409 Conflict`. Use a new key for each logically new submission.

Supported task types: `echo`, `sum`, and `concat`.

- `GET /api/tasks/{task_id}` — retrieve task status.
- `GET /api/tasks/` — list up to 100 recent tasks.
- `GET /health` — liveness.
- `GET /ready` — PostgreSQL readiness.

## Deployment preparation

This is an API service, not a browser-based product website. You can self-host the complete stack on a Docker-capable VPS or private server:

1. Provision a supported Linux host and install Docker Engine plus Compose.
2. Clone this repository and create a private `.env` file.
3. Set unique random `API_KEY` and `POSTGRES_PASSWORD` values, plus broker/database URLs appropriate for the Compose network.
4. Keep API, Redis, and PostgreSQL ports private. Put a TLS reverse proxy (for example Caddy or Nginx) in front of the API and expose only HTTPS.
5. Start with `docker compose up -d --build`; the API applies Alembic migrations before startup.
6. Verify `/health`, `/ready`, submit a test task, and verify its result.
7. Configure encrypted database backups, restore testing, log retention, host monitoring, and key rotation before inviting external users.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the deployment checklist and environment variables. Do not expose Redis or PostgreSQL to the public internet.

## Migrations and tests

```bash
alembic upgrade head
alembic current
alembic downgrade -1
pytest -q
```

CI provisions disposable PostgreSQL and Redis, applies migrations, runs tests, starts a real Celery worker, verifies Redis-to-Celery-to-PostgreSQL execution, and checks migration downgrade.

## Security and known limitations

- API task routes use a shared API key. This is service authentication, not user accounts, role-based access control, or per-user quotas.
- Compose publishes ports on localhost for development. A public deployment requires TLS, network restrictions, rate limiting, and an appropriate secret-management process.
- Task payloads/results are stored in PostgreSQL; never submit credentials, patient data, or other sensitive information.
- Celery uses late acknowledgements and worker-loss rejection to improve redelivery behaviour. Redelivery can still cause duplicate execution; task handlers with external side effects must be idempotent.
- Idempotency keys protect client resubmission, but do not provide exactly-once execution. Durable outbox processing, dead-letter workflows, and crash-recovery drills remain future work.
- Monitoring/metrics, backup/restore drills, rate limiting, and a full local Docker Compose smoke test remain to be completed before production use.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). MIT licensed; see [LICENSE](LICENSE).

## Maintainer

Created and maintained by [TannishtoDasGupta](https://github.com/TannishtoDasGupta).
