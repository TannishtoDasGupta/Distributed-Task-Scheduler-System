# Deployment guide

This project is a FastAPI API and Celery worker stack. It does not include a public-facing end-user website. Interactive API documentation is available at `/docs`.

## Recommended deployment shape

Self-host with Docker Compose on a Docker-capable Linux VPS or private server. Place a maintained TLS reverse proxy (Caddy, Nginx, or an equivalent managed gateway) in front of the API.

1. Provision the host, patch the operating system, and install Docker Engine and the Compose plugin.
2. Clone the repository and create `.env` from `.env.example`.
3. Generate unique secrets locally:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
4. Set `API_KEY` and `POSTGRES_PASSWORD` to independent random values. Keep `.env` readable only by the deployment operator.
5. Confirm `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` use the internal Compose Redis hostname, and PostgreSQL settings use the internal database hostname.
6. Start the stack:
   ```bash
   docker compose up -d --build
   docker compose ps
   docker compose logs --tail=100 web worker
   ```
7. Configure the reverse proxy to forward HTTPS traffic to the API container. Do not expose ports 5432 or 6379 publicly. Restrict SSH and administrative access.
8. Check `/health` and `/ready`, submit a test task with `X-API-Key`, and poll the returned task ID until it reaches a terminal state.
9. Configure automated encrypted PostgreSQL backups, test restores, host monitoring, log retention, dependency update review, and secret rotation.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `API_KEY` | Yes | Shared API authentication secret; at least 32 characters |
| `POSTGRES_USER` | Yes | Database user |
| `POSTGRES_PASSWORD` | Yes | Unique database password |
| `POSTGRES_DB` | Yes | Database name |
| `POSTGRES_HOST` | Yes | Use `db` within Compose |
| `POSTGRES_PORT` | No | Defaults to 5432 |
| `CELERY_BROKER_URL` | Yes | Redis broker URL; use internal Compose hostname |
| `CELERY_RESULT_BACKEND` | Yes | Redis result backend URL |
| `TASK_MAX_RETRIES` | No | Defaults to 3 |

Generate keys locally; do not paste them into GitHub files, commits, issues, or pull requests. If a secret is exposed, rotate it and redeploy.

## Operational caveats

- The shared API key does not provide user accounts, role-based permissions, per-user quotas, or rate limiting.
- Late acknowledgement and worker-loss rejection improve task redelivery, but can cause duplicate execution. Design handlers to tolerate redelivery.
- Client idempotency keys prevent duplicate submissions, not duplicate side effects after worker crashes.
- The current Compose file is a single-host starter, not a highly available production architecture.
- No public service is deployed by this repository change. Live deployment requires the operator to supply secrets and infrastructure.
