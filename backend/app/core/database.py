"""
Async SQLAlchemy engine + session factory.

Local development uses SQLite via aiosqlite.
Production uses Supabase PostgreSQL via asyncpg.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _normalize_database_url(url: str) -> str:
    """Convert postgres URLs to SQLAlchemy async format."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)

    return url


# ------------------------------------------------------------------
# Database URL
# ------------------------------------------------------------------

if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

_db_url = _normalize_database_url(settings.DATABASE_URL)


# ------------------------------------------------------------------
# Engine configuration
# ------------------------------------------------------------------

_engine_kwargs = {
    "echo": False,
    "future": True,
}

if _db_url.startswith("postgresql+asyncpg://"):
    _engine_kwargs.update(
        {
            "connect_args": {
                "ssl": "require",
                "statement_cache_size": 0,
            },
            "poolclass": NullPool,
        }
    )
else:
    # SQLite
    _engine_kwargs["pool_pre_ping"] = True


# ------------------------------------------------------------------
# Engine
# ------------------------------------------------------------------

engine = create_async_engine(
    _db_url,
    **_engine_kwargs,
)


# ------------------------------------------------------------------
# Session Factory
# ------------------------------------------------------------------

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ------------------------------------------------------------------
# Base Model
# ------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ------------------------------------------------------------------
# Dependency
# ------------------------------------------------------------------

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ------------------------------------------------------------------
# Initialize Database
# ------------------------------------------------------------------

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)