# Multi-stage Dockerfile for Nimbus API
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Allow override of DB host for tests
ENV DATABASE_HOST=db

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.3

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy Poetry files
COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock

# --- Development stage ---

# Development stage
FROM base as development

# Copy all source code and required files first
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini
COPY wait_for_db_and_migrate.sh ./wait_for_db_and_migrate.sh

# Configure Poetry to create virtualenv in project
RUN poetry config virtualenvs.in-project true

# Install dependencies including dev dependencies
RUN poetry install

# Don't remove cache - it contains the virtualenv!
# RUN rm -rf $POETRY_CACHE_DIR

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8000

# Entrypoint for dev: wait for DB, migrate, start API
RUN chmod +x ./wait_for_db_and_migrate.sh
CMD ["./wait_for_db_and_migrate.sh"]

# --- Test stage ---
FROM development as test

# Optionally override DB host for CI/local
ARG DATABASE_HOST=localhost
ENV DATABASE_HOST=${DATABASE_HOST}

# Copy test files
COPY tests/ ./tests/

# Run tests (can be overridden in CI)
CMD ["poetry", "run", "pytest", "--maxfail=1", "--disable-warnings"]

# Production stage
FROM base as production

# Copy backend code and config for production (before poetry install)
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini
COPY wait_for_db_and_migrate.sh ./wait_for_db_and_migrate.sh

RUN poetry install --only main --no-cache && rm -rf $POETRY_CACHE_DIR && poetry run pip install uvicorn fastapi sqlalchemy pydantic pydantic-settings python-jose redis structlog slowapi alembic python-multipart cryptography requests opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-sqlalchemy psycopg2-binary email-validator httpx psycopg fastapi-limiter PyJWT asyncpg && poetry run pip list

# Create non-root user
RUN groupadd -r nimbus && useradd -r -g nimbus nimbus

# Set Python path
ENV PYTHONPATH=/app/src

# Switch to non-root user
USER nimbus

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production command with optimizations (use Poetry run)
CMD ["poetry", "run", "uvicorn", "nimbus.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "4", \
    "--access-log", \
    "--log-level", "info"]

# --- Usage notes ---
# To run backend tests in Docker:
#   docker build -t nimbus-api-test --target test .
#   docker run --rm -e DATABASE_HOST=localhost nimbus-api-test
# For CI, override DATABASE_HOST as needed.