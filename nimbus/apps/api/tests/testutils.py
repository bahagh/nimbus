# apps/api/tests/testutils.py
import os
import hmac
import hashlib
import uuid
import datetime as dt

from sqlalchemy import text
from nimbus.db import get_sessionmaker


def hmac_sig(ts: int, method: str, path: str, body: str, secret: str) -> str:
    bh = hashlib.sha256(body.encode()).hexdigest()
    payload = f"{ts}.{method}.{path}.{bh}"
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


async def ensure_project(project_id: str | None = None) -> str:
    """Insert a project row if it doesn't exist; return its id."""
    pid = project_id or str(uuid.uuid4())
    key_id = os.getenv("INGEST_API_KEY_ID", "local-key-id")
    secret = os.getenv("INGEST_API_KEY_SECRET", "local-super-secret")
    api_key_hash = hashlib.sha256(secret.encode()).hexdigest()

    Session = get_sessionmaker()
    async with Session() as s, s.begin():
        # already there?
        exists = await s.execute(text("SELECT 1 FROM projects WHERE id = :id"), {"id": pid})
        if exists.scalar_one_or_none():
            return pid

        # Detect dialect (sqlite vs postgres) without awaiting
        bind = s.get_bind()  # AsyncEngine, not awaitable
        dialect_name = getattr(getattr(bind, "sync_engine", bind), "dialect").name

        if dialect_name == "sqlite":
            stmt = text(
                """
                INSERT OR IGNORE INTO projects (id, name, api_key_id, api_key_hash)
                VALUES (:id, :name, :api_key_id, :api_key_hash)
                """
            )
        else:
            # Postgres
            stmt = text(
                """
                INSERT INTO projects (id, name, api_key_id, api_key_hash)
                VALUES (:id, :name, :api_key_id, :api_key_hash)
                ON CONFLICT (id) DO NOTHING
                """
            )

        await s.execute(
            stmt,
            {
                "id": pid,
                "name": "pytest-project",
                "api_key_id": key_id,
                "api_key_hash": api_key_hash,
            },
        )

    return pid


async def count_events(pid: str) -> int:
    Session = get_sessionmaker()
    async with Session() as s:
        r = await s.execute(text("SELECT count(*) FROM events WHERE project_id=:pid"), {"pid": pid})
        val = r.scalar_one()
        return int(val or 0)
