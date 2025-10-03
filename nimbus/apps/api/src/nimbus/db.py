from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from nimbus.settings import settings
from nimbus.models.base import Base

_engine = None
_sessionmaker = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(str(settings.database_url), pool_pre_ping=True)
    return _engine

def get_sessionmaker():
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    return _sessionmaker

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    Session = get_sessionmaker()
    async with Session() as s:
        yield s
