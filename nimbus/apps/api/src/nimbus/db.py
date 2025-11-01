from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from nimbus.settings import settings
from nimbus.models.base import Base
import logging
import os

logger = logging.getLogger(__name__)

_engine = None
_sessionmaker = None

def get_engine():
    global _engine
    if _engine is None:
        # Enhanced engine configuration for production
        connect_args = {}
        
        # PostgreSQL specific optimizations
        if "postgresql" in settings.get_database_url():
            connect_args.update({
                "server_settings": {
                    "application_name": "nimbus-api",
                    "jit": "off",  # Disable JIT for better connection performance
                }
            })
        
        # Use NullPool in tests to avoid connection pooling issues
        use_null_pool = os.getenv("NIMBUS_USE_NULL_POOL", "false").lower() == "true"
        
        engine_kwargs = {
            "url": settings.get_database_url(),
            "connect_args": connect_args,
            "echo": settings.is_development() and settings.debug,
            "echo_pool": settings.is_development() and settings.debug,
            "query_cache_size": 1200,
        }
        
        if use_null_pool:
            # No connection pooling for tests
            engine_kwargs["poolclass"] = NullPool
            logger.info("Database engine created with NullPool (no connection pooling)")
        else:
            # Production connection pooling
            engine_kwargs.update({
                "pool_size": settings.db_pool_size,
                "max_overflow": settings.db_max_overflow,
                "pool_timeout": settings.db_pool_timeout,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            })
            logger.info(f"Database engine created with pool_size={settings.db_pool_size}, max_overflow={settings.db_max_overflow}")
        
        _engine = create_async_engine(**engine_kwargs)
    
    return _engine

def get_sessionmaker():
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            get_engine(), 
            expire_on_commit=False, 
            class_=AsyncSession,
            # Optimize for bulk operations
            autoflush=False,  # Manual control over when to flush
        )
    return _sessionmaker

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    Session = get_sessionmaker()
    async with Session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Health check function
async def check_database_health() -> bool:
    """Check if database is accessible and responsive"""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Graceful shutdown
async def cleanup_database():
    """Clean up database connections on shutdown"""
    global _engine, _sessionmaker
    if _engine:
        # Force immediate disposal of all connections
        await _engine.dispose()
        logger.info("Database engine disposed")
    _engine = None
    _sessionmaker = None

def reset_engine():
    """Reset engine and sessionmaker (for tests)"""
    global _engine, _sessionmaker
    _engine = None
    _sessionmaker = None

def reset_engine():
    """Synchronously reset the engine and sessionmaker - for tests only"""
    global _engine, _sessionmaker
    _engine = None
    _sessionmaker = None
