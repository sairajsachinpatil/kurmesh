# KURMESH V1

KURMESH is a maritime decision-support system. It currently contains Phase 1 infrastructure and the Phase 2 application foundation: a React health dashboard, Flask API, PostGIS persistence schema, authentication/authorization primitives, audit-event creation, and human route review/approval controls. It contains no environmental provider, ML, routing, simulation-worker, or frontend domain workflow implementation.

## Start locally

1. Install Docker Desktop and ensure it is running.
2. Copy `.env.example` to `.env`.
3. Replace `POSTGRES_PASSWORD` and the matching password in `DATABASE_URL` in `.env`. Set `AUTH_SECRET` to a unique random value of at least 32 characters. The API refuses to start without it.
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

The backend container applies Alembic migrations before serving traffic. The initial migration uses explicit Alembic operations and creates only KURMESH tables and indexes. Its downgrade drops only those objects; it does not remove the PostGIS extension or unrelated database objects.

Run backend checks locally from `backend/`:

```sh
pytest -q
python -m compileall app migrations
alembic upgrade --sql head
alembic downgrade --sql base
```

The clean-PostGIS integration tests run only when `KURMESH_INTEGRATION_DATABASE_URL` names a disposable database. They reset that database's `public` schema, so never point it at operational data.

## Phase 2 API foundation

All API routes are under `/api/v1`. Health routes are public. The domain API has request-scoped SQLAlchemy sessions; domain endpoints require Bearer authentication unless otherwise indicated. Account creation creates no privileged role. Roles must be assigned through an approved administrative process outside this API foundation.

Mission mutations require the mission owner or an `admin` role. Mission state changes use the explicit state graph in the API. Route approval requires an `operator` or `admin`, an existing human review, and a different reviewer and approver. Audit events are created by mutations and have no write, update, or delete API endpoints.

## Environment and safety

Use `.env.example` only as a template; never commit `.env`. The provided password is deliberately a placeholder and fails Compose interpolation until replaced. Production requires a secrets manager, TLS/reverse proxy configuration, restricted CORS origins, backups, and authenticated API domains in later phases.

## Repository layout

- `frontend/`: React/Vite health dashboard and API health integration.
- `backend/`: Flask API, explicit Alembic migration, PostGIS models, auth foundation, dependency health probes, structured logging, and Celery configuration.
- `workers/`: reserved for task-domain modules as worker behavior grows.
- `database/`: reserved; Alembic migrations live in `backend/migrations/`.
- `ml/`, `routing/`, `data/`, `models/`: reserved; no providers, artifacts, or fabricated outputs exist here.
- `tests/`: cross-service and end-to-end tests added in later phases.
