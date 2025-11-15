# Nimbus Analytics

A high-performance event analytics API built with FastAPI, PostgreSQL, and Redis. Nimbus provides real-time event ingestion, querying, and metrics aggregation for modern applications.

## Features

- **Fast Event Ingestion**: Batch event processing with HMAC authentication
- **Real-time Metrics**: Time-series analytics with customizable bucketing
- **Secure Authentication**: JWT-based user authentication and project-level API keys
- **Flexible Querying**: Filter events by name, user, timestamp, and custom properties
- **Redis Caching**: Optional caching layer for improved performance
- **OpenAPI Documentation**: Auto-generated interactive API docs

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 14 with async SQLAlchemy
- **Cache**: Redis 7
- **Frontend**: React with TypeScript
- **Deployment**: Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- Node.js 18+ (for frontend development)

### Running with Docker

```bash
# Clone the repository
git clone https://github.com/bahagh/nimbus.git
cd nimbus

# Start all services
cd deploy/docker
docker-compose -f compose.dev.yml up -d

# Check service health
docker-compose -f compose.dev.yml ps
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Usage

### 1. Register & Login

```bash
# Register a new user
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'

# Login to get JWT token
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'
```

### 2. Create a Project

```bash
# Create project (returns API keys)
curl -X POST http://localhost:8000/v1/projects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My App","description":"Production analytics"}'
```

### 3. Ingest Events

Events are ingested using HMAC signatures for security:

```bash
# Example event ingestion (see docs for HMAC signature generation)
curl -X POST http://localhost:8000/v1/events \
  -H "Content-Type: application/json" \
  -H "x-api-key-id: YOUR_API_KEY_ID" \
  -H "x-api-timestamp: UNIX_TIMESTAMP" \
  -H "x-api-signature: HMAC_SIGNATURE" \
  -d '{
    "project_id": "PROJECT_UUID",
    "events": [{
      "name": "page_view",
      "ts": "2024-01-15T10:30:00Z",
      "props": {"page": "/home", "referrer": "google"},
      "user_id": "user123"
    }]
  }'
```

### 4. Query Events

```bash
# List events with filtering
curl -X GET "http://localhost:8000/v1/events?project_id=PROJECT_UUID&limit=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5. Get Metrics

```bash
# Get time-series metrics
curl -X GET "http://localhost:8000/v1/metrics?project_id=PROJECT_UUID&bucket=1h&limit=24" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Development

### Local API Development

```bash
cd apps/api

# Install dependencies
poetry install

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn nimbus.main:app --reload
```

### Running Tests

```bash
cd apps/api
poetry run pytest
```

### Environment Variables

Create a `.env` file in `apps/api/`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/nimbus

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=your-secret-key-min-32-chars-long
INGEST_API_KEY_SECRET=your-ingest-secret

# Optional
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10000
```

## Project Structure

```
nimbus/
├── apps/
│   ├── api/              # FastAPI backend
│   │   ├── src/nimbus/
│   │   │   ├── routes/   # API endpoints
│   │   │   ├── models/   # SQLAlchemy models
│   │   │   ├── schemas/  # Pydantic schemas
│   │   │   ├── services/ # Business logic
│   │   │   ├── security/ # Auth & HMAC
│   │   │   └── main.py   # App entry point
│   │   ├── alembic/      # Database migrations
│   │   └── tests/        # Unit tests
│   └── worker/           # Background jobs (future)
├── frontend/             # React UI
├── deploy/
│   └── docker/          # Docker Compose configs
└── README.md
```

## Architecture

- **Async I/O**: Non-blocking database and cache operations
- **Connection Pooling**: Efficient resource management
- **HMAC Authentication**: Secure event ingestion without exposing secrets
- **Rate Limiting**: Built-in protection against abuse
- **Health Checks**: Automated monitoring endpoints

## Performance

- Event ingestion: <200ms p99 latency
- Batch processing: 1000+ events/request
- Query response: <100ms for most queries
- Metrics aggregation: Real-time with 1-hour granularity

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using FastAPI and PostgreSQL**
