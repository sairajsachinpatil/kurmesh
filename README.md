# KURMESH V1

KURMESH is a maritime decision-support system. This repository currently implements **Phase 1 infrastructure only**: a React frontend, Flask API, PostGIS database, Redis, and a Celery worker. It contains no missions, routes, environmental observations, ML predictions, or scientific demo data.

## Start locally

1. Install Docker Desktop and ensure it is running.
2. Copy `.env.example` to `.env`.
3. Replace `POSTGRES_PASSWORD` and the matching password in `DATABASE_URL` in `.env`.
4. From the repository root, run:

```sh
docker compose up --build
```

Open `http://localhost`. The UI requests `GET /api/v1/health` through Nginx; no browser-side API host configuration is necessary in Compose.

## Validate

```sh
docker compose config
docker compose up --build -d
curl http://localhost/api/v1/health
docker compose ps
docker compose logs --tail=100 backend worker
docker compose down
```

The API checks PostgreSQL connectivity, the installed PostGIS extension, and Redis reachability. `GET /api/v1/health/live` is dependency-free; `GET /api/v1/health/ready` returns 503 until required dependencies are ready.

## Local non-container frontend build

```sh
cd frontend
npm ci
npm run build
```

## Backend tests and migrations

```sh
docker compose run --rm backend pytest
docker compose exec backend alembic current
```

The backend container applies Alembic migrations before serving traffic. The clean-PostGIS migration integration test runs when `KURMESH_INTEGRATION_DATABASE_URL` points to a disposable database; it is intentionally skipped without that explicit database to avoid erasing a non-test database.

## Environment and safety

Use `.env.example` only as a template; never commit `.env`. The provided password is deliberately a placeholder and fails Compose interpolation until replaced. Production requires a secrets manager, TLS/reverse proxy configuration, restricted CORS origins, backups, and authenticated API domains in later phases.

## Repository layout

- `frontend/`: React/Vite dashboard shell and API health integration.
- `backend/`: Flask API, dependency health probes, structured logging, and Celery configuration.
- `workers/`: reserved for task-domain modules as worker behavior grows.
- `database/`: reserved for Alembic migrations, introduced with the Phase 3 data model.
- `ml/`, `routing/`, `data/`, `models/`: reserved; no artifacts or fabricated outputs exist here.
- `tests/`: cross-service and end-to-end tests added in later phases.
