# Multi-stage Dockerfile for Nimbus Worker
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
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
COPY pyproject.toml poetry.lock ./

# Development stage
FROM base as development

# Install dependencies including dev dependencies
RUN poetry install && rm -rf $POETRY_CACHE_DIR

# Copy source code
COPY . .

# Development command
CMD ["poetry", "run", "python", "-m", "nimbus_worker.worker"]

# Production stage
FROM base as production

# Install only production dependencies
RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

# Create non-root user
RUN groupadd -r nimbus && useradd -r -g nimbus nimbus

# Copy source code
COPY --chown=nimbus:nimbus . .

# Switch to non-root user
USER nimbus

# Production command
CMD ["poetry", "run", "python", "-m", "nimbus_worker.worker"]