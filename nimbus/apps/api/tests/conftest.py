# apps/api/tests/conftest.py
import os
import pytest

# ---- Test env defaults ----
os.environ["NIMBUS_DATABASE_URL"] = "postgresql+asyncpg://postgres:baha123@localhost:5432/nimbus_test"
os.environ.setdefault("NIMBUS_JWT_SECRET", "testsecret-must-be-at-least-32-chars-long-for-security")
os.environ.setdefault("NIMBUS_JWT_ALGORITHM", "HS256")
os.environ.setdefault("NIMBUS_RATE_LIMIT_PER_MINUTE", "1000")
os.environ.setdefault("NIMBUS_INGEST_API_KEY_ID", "local-key-id")
os.environ.setdefault("NIMBUS_INGEST_API_KEY_SECRET", "local-super-secret")
os.environ.setdefault("NIMBUS_REDIS_URL", "redis://localhost:6379/0")
# Use NullPool to avoid connection pooling issues in tests
os.environ.setdefault("NIMBUS_USE_NULL_POOL", "true")

from src.nimbus.db import get_engine  # noqa: E402
from src.nimbus.models.base import Base  # noqa: E402
# Import models so they register with Base.metadata
import src.nimbus.models.user    # noqa: F401,E402
import src.nimbus.models.project # noqa: F401,E402
import src.nimbus.models.event   # noqa: F401,E402
from src.nimbus.main import app  # noqa: F401,E402  # keep app import working for tests

import pytest_asyncio


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_db_connections():
    """Clean up database connections after each test."""
    yield
    # Clean up after the test finishes
    from src.nimbus.db import reset_engine
    try:
        reset_engine()
    except Exception:
        pass
