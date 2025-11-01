# Nimbus API Backend

A FastAPI backend for event analytics, with JWT authentication, HMAC event ingestion, and robust migrations.

## Features
- Secure registration and login (JWT)
- Event ingestion (HMAC-signed)
- Event listing (JWT-protected)
- PostgreSQL + SQLAlchemy (async)
- Alembic migrations
- Redis caching

## Manual Migration & Index Fixes

If you encounter migration or index errors, follow these steps:

### 1. Run Alembic Migrations
```sh
cd apps/api
poetry run alembic upgrade head
```

### 2. Manually Create Performance Indexes
Connect to your PostgreSQL database and run:
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_events_project_ts_desc ON events(project_id, ts DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_events_project_user_ts ON events(project_id, user_id, ts DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_events_project_name_ts ON events(project_id, name, ts DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_events_props_gin ON events USING GIN(props jsonb_path_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_events_recent ON events(project_id, ts DESC) WHERE ts > (NOW() - INTERVAL '30 days');
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_events_idempotency_key ON events(project_id, idempotency_key);
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_projects_created_at ON projects(created_at DESC);
```

### 3. Fix Migration Errors
If a migration fails, check the Alembic migration files in `apps/api/alembic/versions/` and ensure SQL syntax matches PostgreSQL requirements.

## API Endpoints
- `POST /v1/auth/register` — Register new user
- `POST /v1/auth/login` — Login and get JWT
- `POST /v1/events` — Ingest events (HMAC required)
- `GET /v1/events` — List events (JWT required)
- `GET /health` — Health check

## Environment Variables
See `.env.example` for required variables.

## Running Locally
```sh
cd apps/api
poetry install
poetry run uvicorn nimbus.main:app --reload
```

## Docker/Compose
See `deploy/docker/compose.dev.yml` for multi-service orchestration.

---
For more details, see the main project README.