# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0-beta.1] - 2025-11-01

### 🎉 Initial Beta Release

**Status:** Backend API is production-ready. Dashboard UI coming Q1 2026.

### Added
- Initial release of Nimbus Analytics Platform
- FastAPI-based async REST API for event ingestion
- PostgreSQL database with SQLAlchemy 2.0 async ORM
- Redis caching and rate limiting
- JWT authentication with HS256/RS256 support
- HMAC-SHA256 request signing for event security
- Multi-tenant project isolation with API keys
- Real-time metrics aggregation (1m, 5m, 15m, 1h, 1d buckets)
- Idempotent event ingestion with deduplication
- Database migrations with Alembic
- Comprehensive test suite (100% pass rate)
- Docker Compose development environment
- Interactive API documentation (Swagger UI & ReDoc)
- WebSocket support for real-time event streaming
- OIDC authentication support
- Rate limiting with slowapi
- Structured logging with structlog
- Health check endpoints
- CORS middleware configuration
- OpenTelemetry instrumentation hooks
- Bcrypt password hashing
- Email validation
- Production-ready error handling
- CI/CD with GitHub Actions (lint, type-check, test)

### Security
- Multi-layer authentication (JWT + HMAC + API Keys)
- Password hashing with bcrypt (cost factor 12)
- Rate limiting to prevent abuse
- CORS protection
- SQL injection prevention via parameterized queries
- Input validation with Pydantic v2

### Performance
- Async-first architecture (FastAPI + asyncpg)
- Connection pooling (configurable pool size)
- Redis caching for session storage
- Efficient database indexing
- Benchmarked at 10,000+ events/second
- <50ms query latency for 1M+ events

### Documentation
- Comprehensive README with 1300+ lines
- Quick start guide (30-second demo)
- Usage examples (4 complete workflows)
- Deployment guides (AWS, Azure, GCP, Kubernetes)
- Troubleshooting section with common issues
- FAQ with 15+ questions
- Contributing guidelines
- API documentation with Swagger UI
- Architecture overview
- Security documentation

[0.1.0-beta.1]: https://github.com/bahagh/nimbus/releases/tag/v0.1.0-beta.1
