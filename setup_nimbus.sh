#!/usr/bin/env bash
set -euo pipefail

# --------- 0) Prereqs check (best-effort) ----------
command -v python >/dev/null || { echo "Python is required"; exit 1; }
command -v pip >/dev/null || { echo "pip is required"; exit 1; }
command -v docker >/dev/null || { echo "Docker is required"; exit 1; }
command -v docker compose >/dev/null || { echo "Docker Compose v2 is required"; exit 1; }
if ! command -v poetry >/dev/null; then
  python -m pip install --user poetry==1.8.3
  export PATH="$HOME/.local/bin:$PATH"
fi

# --------- 1) Skeleton repo ----------
mkdir -p nimbus/apps/api/src/nimbus/{security,models,schemas,repositories,routes,tasks} \
         nimbus/apps/worker/src/nimbus_worker \
         nimbus/deploy/docker \
         nimbus/apps/api/alembic/versions \
         nimbus/.github/workflows \
         nimbus/apps/api/tests
cd nimbus

# --------- 2) Root files ----------
cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.env
.env.*
.poetry/
.cache/
dist/
.mypy_cache/
.pytest_cache/
.idea/
.vscode/
**/__pycache__/
EOF

cat > Makefile <<'EOF'
.PHONY: bootstrap up down dev-api dev-worker lint type fmt db-migrate db-upgrade db-downgrade test

bootstrap:
	poetry -C apps/api install
	poetry -C apps/worker install

up:
	docker compose -f deploy/docker/compose.dev.yml up -d
	@sleep 2
	@echo "Postgres + Redis are up"

down:
	docker compose -f deploy/docker/compose.dev.yml down -v

dev-api:
	poetry -C apps/api run uvicorn nimbus.main:app --reload --host 0.0.0.0 --port 8000

dev-worker:
	poetry -C apps/worker run python -m nimbus_worker.worker

lint:
	poetry -C apps/api run black --check src tests
	poetry -C apps/api run isort --check-only src tests
	poetry -C apps/api run flake8
	poetry -C apps/api run mypy src

fmt:
	poetry -C apps/api run black src tests
	poetry -C apps/api run isort src tests

type:
	poetry -C apps/api run mypy src

db-migrate:
	cd apps/api && poetry run alembic revision -m "$(msg)" --autogenerate

db-upgrade:
	cd apps/api && poetry run alembic upgrade head

db-downgrade:
	cd apps/api && poetry run alembic downgrade -1

test:
	poetry -C apps/api run pytest -q
EOF

# --------- 3) Docker compose for local infra ----------
cat > deploy/docker/compose.dev.yml <<'EOF'
version: '3.9'
services:
  db:
    image: postgres:14
    container_name: nimbus-db
    environment:
      POSTGRES_PASSWORD: baha123
      POSTGRES_USER: postgres
      POSTGRES_DB: nimbus
    ports: ["5432:5432"]
    healthcheck:
      test: ["CMD-SHELL","pg_isready -U postgres -d nimbus"]
      interval: 5s
      timeout: 5s
      retries: 10
  redis:
    image: redis:7
    container_name: nimbus-redis
    ports: ["6379:6379"]
EOF

# --------- 4) API pyproject ----------
cat > apps/api/pyproject.toml <<'EOF'
[tool.poetry]
name = "nimbus-api"
version = "0.1.0"
description = "Nimbus FastAPI backend"
authors = ["baha.ghrissi@esprit.tn"]
package-mode = true
packages = [{ include = "nimbus", from = "src" }]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115.0"
uvicorn = {extras=["standard"], version="^0.30.0"}
sqlalchemy = "^2.0.32"
asyncpg = "^0.29.0"
pydantic = "^2.8.2"
pydantic-settings = "^2.4.0"
pyjwt = "^2.8.0"
bcrypt = "^4.1.3"
redis = "^5.0.7"
structlog = "^24.1.0"
slowapi = "^0.1.9"
alembic = "^1.13.2"
httpx = "^0.27.0"
python-multipart = "^0.0.9"
cryptography = "^43.0.0"
# OIDC/JWKS support
python-jose = "^3.3.0"
requests = "^2.32.3"
# Observability
opentelemetry-api = "^1.26.0"
opentelemetry-sdk = "^1.26.0"
opentelemetry-instrumentation-fastapi = "^0.47b0"
opentelemetry-instrumentation-sqlalchemy = "^0.47b0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.2"
pytest-asyncio = "^0.23.8"
black = "^24.8.0"
flake8 = "^7.1.1"
isort = "^5.13.2"
mypy = "^1.11.2"

[tool.black]
line-length = 100

[tool.isort]
profile = "black"

[tool.mypy]
python_version = "3.12"
strict = true
EOF

# --------- 5) API: env example ----------
cat > apps/api/.env.example <<'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:baha123@localhost:5432/nimbus
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=change-me-local
JWT_ALG=HS256
CORS_ORIGINS=http://localhost:5173
RATE_LIMIT_PER_MINUTE=120

# API Key/HMAC (server-side secrets; store only hashes in DB in real apps)
INGEST_API_KEY_ID=local-key-id
INGEST_API_KEY_SECRET=local-super-secret

# Optional OIDC (set these to enable RS256 validation via JWKS)
OIDC_ISSUER=https://YOUR_DOMAIN/.well-known/openid-configuration
OIDC_AUDIENCE=your-api-audience
EOF

# --------- 6) API: config/logging/db/cache ----------
cat > apps/api/src/nimbus/config.py <<'EOF'
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List, Optional

class Settings(BaseSettings):
    app_name: str = "nimbus-api"
    environment: str = "dev"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    # auth
    jwt_secret: str
    jwt_alg: str = "HS256"
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 1209600

    # api key / hmac
    ingest_api_key_id: Optional[str] = None
    ingest_api_key_secret: Optional[str] = None

    # oidc (optional)
    oidc_issuer: Optional[str] = None
    oidc_audience: Optional[str] = None

    cors_origins: List[AnyHttpUrl] = []
    rate_limit_per_minute: int = 120

    class Config:
        env_file = ".env"

settings = Settings()
EOF

cat > apps/api/src/nimbus/logging.py <<'EOF'
import logging, sys, structlog

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
EOF

cat > apps/api/src/nimbus/db.py <<'EOF'
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from .config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

@asynccontextmanager
async def session_scope():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
EOF

cat > apps/api/src/nimbus/cache.py <<'EOF'
import redis.asyncio as aioredis
from .config import settings
redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
EOF

# --------- 7) Models ----------
cat > apps/api/src/nimbus/models/base.py <<'EOF'
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Timestamped:
    created_at: Mapped[object] = mapped_column(server_default=func.now())
    updated_at: Mapped[object] = mapped_column(server_default=func.now(), onupdate=func.now())

class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
EOF

cat > apps/api/src/nimbus/models/user.py <<'EOF'
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from ..db import Base
from .base import UUIDMixin, Timestamped

class User(Base, UUIDMixin, Timestamped):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
EOF

cat > apps/api/src/nimbus/models/project.py <<'EOF'
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from ..db import Base
from .base import UUIDMixin, Timestamped

class Project(Base, UUIDMixin, Timestamped):
    __tablename__ = "projects"
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    api_key_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    api_key_hash: Mapped[str] = mapped_column(String(255))
EOF

cat > apps/api/src/nimbus/models/event.py <<'EOF'
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from ..db import Base
from .base import UUIDMixin

class Event(Base, UUIDMixin):
    __tablename__ = "events"
    project_id: Mapped[object] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    ts: Mapped[object] = mapped_column(TIMESTAMP(timezone=True), index=True)
    props: Mapped[dict] = mapped_column(JSONB)
    user_id: Mapped[str | None]
    seq: Mapped[int | None] = mapped_column(BigInteger)
EOF

# --------- 8) Schemas ----------
cat > apps/api/src/nimbus/schemas/auth.py <<'EOF'
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str
EOF

cat > apps/api/src/nimbus/schemas/event.py <<'EOF'
from pydantic import BaseModel, Field
from typing import Any, List, Optional
from datetime import datetime

class EventIn(BaseModel):
    name: str
    ts: datetime
    props: dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    seq: Optional[int] = None

class EventsIn(BaseModel):
    project_id: str
    events: List[EventIn]
EOF

cat > apps/api/src/nimbus/schemas/metrics.py <<'EOF'
from pydantic import BaseModel

class MetricPoint(BaseModel):
    ts: str
    value: int

class MetricsOut(BaseModel):
    series: list[MetricPoint]
EOF

# --------- 9) Security: JWT, OIDC/JWKS, API Key/HMAC ----------
cat > apps/api/src/nimbus/security/auth.py <<'EOF'
import time, bcrypt, jwt, json, requests
from typing import Optional
from jose.utils import base64url_decode
from .oidc import OIDCVerifier
from ..config import settings

_verifier = None

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def create_token(sub: str, ttl: int) -> str:
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + ttl, "aud": settings.oidc_audience or "nimbus-local"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

def decode_token(token: str) -> Optional[dict]:
    # Prefer OIDC/JWKS if configured (RS256)
    global _verifier
    if settings.oidc_issuer and settings.oidc_audience:
        if _verifier is None:
            _verifier = OIDCVerifier(issuer=settings.oidc_issuer, audience=settings.oidc_audience)
        return _verifier.verify(token)
    # Fallback to local HS256/HS512
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg], audience=settings.oidc_audience or "nimbus-local")
    except Exception:
        return None
EOF

cat > apps/api/src/nimbus/security/oidc.py <<'EOF'
import requests, jwt
from typing import Optional
from functools import lru_cache

class OIDCVerifier:
    def __init__(self, issuer: str, audience: str):
        self.issuer = issuer
        self.audience = audience
        self._cfg = requests.get(issuer, timeout=5).json()
        self._jwks = requests.get(self._cfg["jwks_uri"], timeout=5).json()

    @lru_cache(maxsize=128)
    def _kid_to_key(self, kid: str):
        for k in self._jwks["keys"]:
            if k["kid"] == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(k)
        raise ValueError("kid not found")

    def verify(self, token: str) -> Optional[dict]:
        unverified = jwt.get_unverified_header(token)
        key = self._kid_to_key(unverified["kid"])
        return jwt.decode(token, key=key, algorithms=["RS256"], audience=self.audience)
EOF

cat > apps/api/src/nimbus/security/deps.py <<'EOF'
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth import decode_token
from .hmac import verify_hmac_request

auth_scheme = HTTPBearer(auto_error=False)

async def current_user(creds: HTTPAuthorizationCredentials | None = Depends(auth_scheme)) -> str:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return payload["sub"]

async def require_hmac(request: Request):
    if not await verify_hmac_request(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid signature")
EOF

cat > apps/api/src/nimbus/security/hmac.py <<'EOF'
import hmac, hashlib, time
from fastapi import Request
from ..config import settings

# Expect headers: X-Api-Key-Id, X-Api-Timestamp (unix), X-Api-Signature (hex)
# Signature = HMAC_SHA256(secret, f"{timestamp}.{method}.{path}.{sha256hex(body)}")
ALLOWED_DRIFT = 300  # 5 min

async def verify_hmac_request(request: Request) -> bool:
    if not settings.ingest_api_key_id or not settings.ingest_api_key_secret:
        return False
    key_id = request.headers.get("X-Api-Key-Id")
    ts = request.headers.get("X-Api-Timestamp")
    sig = request.headers.get("X-Api-Signature")
    if not key_id or not ts or not sig:
        return False
    if key_id != settings.ingest_api_key_id:
        return False
    try:
        ts_i = int(ts)
    except Exception:
        return False
    if abs(int(time.time()) - ts_i) > ALLOWED_DRIFT:
        return False
    body_bytes = await request.body()
    body_hash = hashlib.sha256(body_bytes).hexdigest()
    payload = f"{ts}.{request.method.upper()}.{request.url.path}.{body_hash}"
    expected = hmac.new(settings.ingest_api_key_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)
EOF

# --------- 10) Repositories ----------
cat > apps/api/src/nimbus/repositories/events.py <<'EOF'
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.event import Event

async def bulk_insert_events(session: AsyncSession, records: list[dict]):
    if not records:
        return
    stmt = pg_insert(Event).values(records)
    if "seq" in records[0]:
        stmt = stmt.on_conflict_do_nothing(index_elements=[Event.project_id, Event.seq])
    await session.execute(stmt)
EOF

cat > apps/api/src/nimbus/repositories/metrics.py <<'EOF'
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

QUERY = """
SELECT date_trunc(:window, ts) as bucket, count(*)::int as value
FROM events WHERE project_id = :pid AND ts >= now() - :range::interval
GROUP BY 1 ORDER BY 1;
"""

async def fetch_metrics(session: AsyncSession, project_id: str, time_range: str = "24 hours", window: str = "hour"):
    res = await session.execute(text(QUERY), {"pid": project_id, "range": time_range, "window": window})
    return [{"ts": r.bucket.isoformat(), "value": r.value} for r in res]
EOF

# --------- 11) Routes ----------
cat > apps/api/src/nimbus/routes/health.py <<'EOF'
from fastapi import APIRouter
router = APIRouter()
@router.get("/healthz")
async def healthz():
    return {"status": "ok"}
EOF

cat > apps/api/src/nimbus/routes/auth.py <<'EOF'
from fastapi import APIRouter, HTTPException
from ..schemas.auth import LoginIn, Token
from ..security.auth import create_token

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(body: LoginIn):
    # demo only – replace with real user lookup
    if body.email and body.password:
        return Token(
            access_token=create_token(body.email, ttl=900),
            refresh_token=create_token(body.email, ttl=1209600),
        )
    raise HTTPException(status_code=401, detail="invalid credentials")
EOF

cat > apps/api/src/nimbus/routes/events.py <<'EOF'
from fastapi import APIRouter, Depends, Request
from ..schemas.event import EventsIn
from ..security.deps import require_hmac
from ..db import session_scope
from ..repositories.events import bulk_insert_events

router = APIRouter(prefix="/v1/events", tags=["events"])

@router.post("", dependencies=[Depends(require_hmac)])
async def ingest_bulk(body: EventsIn, request: Request):
    records = [dict(project_id=body.project_id, **e.model_dump()) for e in body.events]
    async with session_scope() as s:
        await bulk_insert_events(s, records)
    return {"status": "accepted", "count": len(records)}
EOF

cat > apps/api/src/nimbus/routes/metrics.py <<'EOF'
from fastapi import APIRouter, Query, Depends
from ..cache import redis
from ..db import session_scope
from ..repositories.metrics import fetch_metrics
from ..schemas.metrics import MetricsOut
from ..security.deps import current_user
import json

router = APIRouter(prefix="/v1/metrics", tags=["metrics"])

@router.get("", response_model=MetricsOut, dependencies=[Depends(current_user)])
async def metrics(project_id: str, range: str = Query("24 hours")):
    key = f"metrics:{project_id}:{range}"
    cached = await redis.get(key)
    if cached:
        return MetricsOut(**json.loads(cached))
    async with session_scope() as s:
        data = await fetch_metrics(s, project_id, time_range=range)
    payload = {"series": data}
    await redis.setex(key, 30, json.dumps(payload))
    return payload
EOF

cat > apps/api/src/nimbus/routes/ws.py <<'EOF'
from fastapi import APIRouter, WebSocket
from ..cache import redis

router = APIRouter()

@router.websocket("/ws/projects/{project_id}")
async def ws_metrics(ws: WebSocket, project_id: str):
    await ws.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"metrics:{project_id}")
    try:
        async for msg in pubsub.listen():
            if msg.get("type") == "message":
                await ws.send_text(msg["data"])
    finally:
        await pubsub.unsubscribe(f"metrics:{project_id}")
EOF

# --------- 12) App entrypoint ----------
cat > apps/api/src/nimbus/main.py <<'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .logging import setup_logging
from .routes import health, auth, events, metrics, ws
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.extension import Limiter
from slowapi.util import get_remote_address

setup_logging()
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])

app = FastAPI(title="Nimbus API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=[str(o) for o in settings.cors_origins],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(metrics.router)
# ws routes are registered by path only
EOF

# --------- 13) Alembic ----------
cat > apps/api/alembic.ini <<'EOF'
[alembic]
script_location = alembic
sqlalchemy.url = %(DATABASE_URL)s

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
EOF

cat > apps/api/alembic/env.py <<'EOF'
from logging.config import fileConfig
from alembic import context
import os
from sqlalchemy import create_engine
from nimbus.db import Base
from nimbus.models import user, project, event  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

def run_migrations_offline():
    url = os.getenv("DATABASE_URL")
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    url = os.getenv("DATABASE_URL")
    connectable = create_engine(url.replace("+asyncpg",""))
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF

cat > apps/api/alembic/versions/0001_init.py <<'EOF'
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("api_key_id", sa.String(length=100), nullable=False, unique=True),
        sa.Column("api_key_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_projects_name", "projects", ["name"], unique=True)
    op.create_index("ix_projects_key_id", "projects", ["api_key_id"], unique=True)

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), index=True),
        sa.Column("name", sa.String(length=100), index=True),
        sa.Column("ts", sa.TIMESTAMP(timezone=True), index=True),
        sa.Column("props", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("seq", sa.BigInteger(), nullable=True),
    )
    op.create_index("ix_events_project_ts", "events", ["project_id", "ts"])

def downgrade():
    op.drop_table("events")
    op.drop_table("projects")
    op.drop_table("users")
EOF

# --------- 14) Worker ----------
cat > apps/worker/pyproject.toml <<'EOF'
[tool.poetry]
name = "nimbus-worker"
version = "0.1.0"
description = "Nimbus background worker"
authors = ["baha.ghrissi@esprit.tn"]
packages = [{ include = "nimbus_worker", from = "src" }]

[tool.poetry.dependencies]
python = "^3.12"
sqlalchemy = "^2.0.32"
asyncpg = "^0.29.0"
redis = "^5.0.7"
pydantic-settings = "^2.4.0"
EOF

cat > apps/worker/src/nimbus_worker/config.py <<'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    class Config: env_file = "../../api/.env"

settings = Settings()
EOF

cat > apps/worker/src/nimbus_worker/worker.py <<'EOF'
import asyncio, json
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from .config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

async def rollup_last_minute():
    async with SessionLocal() as s:
        rows = (await s.execute(text("""
            SELECT project_id, date_trunc('minute', ts) AS bucket, count(*)::int AS value
            FROM events WHERE ts > now() - interval '2 minutes'
            GROUP BY 1,2
        """))).all()
    for r in rows:
        payload = json.dumps({"series": [{"ts": r.bucket.isoformat(), "value": r.value}]})
        await redis.publish(f"metrics:{r.project_id}", payload)

async def scheduler():
    while True:
        await rollup_last_minute()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(scheduler())
EOF

# --------- 15) Minimal tests ----------
cat > apps/api/tests/conftest.py <<'EOF'
import pytest
from httpx import AsyncClient
from nimbus.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
EOF

cat > apps/api/tests/test_auth.py <<'EOF'
from nimbus.security.auth import create_token, decode_token

def test_token_cycle():
    token = create_token("user@example.com", 60)
    payload = decode_token(token)
    assert payload and payload["sub"] == "user@example.com"
EOF

# --------- 16) Done banner ----------
echo "Repo scaffolded."

# --------- 17) Bootstrap & run ----------
cp apps/api/.env.example apps/api/.env
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/nimbus"
export REDIS_URL="redis://localhost:6379/0"

make bootstrap
make up

# Run alembic with env picking up .env
( cd apps/api && DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/nimbus" poetry run alembic upgrade head )

echo "Starting API and Worker (leave running in separate shells):"
echo "  make dev-api"
echo "  make dev-worker"
echo
echo "Auth (demo): POST /v1/auth/login"
echo "Ingest (HMAC): POST /v1/events with X-Api-Key-* headers"
echo "Metrics (JWT/OIDC): GET /v1/metrics?project_id=..."
