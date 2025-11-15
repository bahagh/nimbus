#!/bin/sh
set -e

# Wait for database with simple sleep (DB has health check anyway)
echo "Waiting for database..."
sleep 10

# Run Alembic migrations (skip for now - tables created manually)
echo "Skipping migrations (tables already created)..."
# poetry run alembic upgrade head

# Start API
echo "Starting API..."
# Use poetry run - it handles the virtualenv internally
exec poetry run python -m uvicorn nimbus.main:app --host 0.0.0.0 --port 8000 --reload
