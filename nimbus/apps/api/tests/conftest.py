# apps/api/tests/conftest.py
import os
import pytest

# ---- Test env defaults ----
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./tests.db")
os.environ.setdefault("JWT_SECRET", "testsecret")
os.environ.setdefault("JWT_ALG", "HS256")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "1000")
os.environ.setdefault("INGEST_API_KEY_ID", "local-key-id")
os.environ.setdefault("INGEST_API_KEY_SECRET", "local-super-secret")

# Clean stale sqlite file between runs to avoid leftover schema/content
if os.environ["DATABASE_URL"].startswith("sqlite+aiosqlite:///"):
    path = os.environ["DATABASE_URL"].replace("sqlite+aiosqlite:///", "", 1)
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass

from nimbus.db import get_engine  # noqa: E402
from nimbus.models.base import Base  # noqa: E402

# Import models so they register with Base.metadata
import nimbus.models.user    # noqa: F401,E402
import nimbus.models.project # noqa: F401,E402
import nimbus.models.event   # noqa: F401,E402

from nimbus.main import app  # noqa: F401,E402  # keep app import working for tests

import pytest_asyncio


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_schema():
    """Create/drop all tables once per test session using the running event loop."""
    engine = get_engine()
    async with engine.begin() as conn:
        # enforce FKs on sqlite if supported
        try:
            await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        except Exception:
            pass
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
