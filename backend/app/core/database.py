"""
Async SQLAlchemy engine + session factory.

We use SQLite via aiosqlite by default so the project runs with zero
external services (matches SRS NFR: local-first storage). Swapping to
PostgreSQL later is a one-line DATABASE_URL change since we never use
SQLite-specific SQL anywhere in the codebase.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency yielding a scoped async session per request."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Create all tables on startup. Fine for SQLite/demo; use Alembic for prod."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
