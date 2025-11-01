#!/bin/sh
set -e

# Wait for PostgreSQL
DB_HOST="${NIMBUS_DATABASE_HOST:-db}"
DB_PORT="${NIMBUS_DATABASE_PORT:-5432}"
DB_USER="${NIMBUS_DATABASE_USER:-postgres}"
DB_NAME="${NIMBUS_DATABASE_NAME:-nimbus}"
DB_PASS="${NIMBUS_DATABASE_PASSWORD:-baha123}"

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
  sleep 2
done

# Run Alembic migrations
poetry run alembic upgrade head

# Start API (production-ready)
exec poetry run uvicorn nimbus.main:app --host 0.0.0.0 --port 8000 --workers 4 --access-log --log-level info
