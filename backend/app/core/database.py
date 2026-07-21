"""
Async SQLAlchemy engine + session factory.

Local dev uses SQLite via aiosqlite (zero setup). Production uses Supabase
Postgres via asyncpg. Supabase gives you a connection string that starts
with `postgresql://` - SQLAlchemy's async engine needs the driver spelled
out (`postgresql+asyncpg://`), so we normalize that here rather than
requiring you to hand-edit the URL Supabase gives you.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from sqlalchemy.pool import NullPool


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):  # some providers use this shorthand
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


_engine_kwargs = {"echo": False, "future": True}
_db_url = _normalize_database_url(settings.DATABASE_URL)

if _db_url.startswith("postgresql+asyncpg://"):
    # Supabase's pooler (PgBouncer, transaction mode) is incompatible with
    # asyncpg's prepared-statement caching and connection reuse. NullPool
    # avoids SQLAlchemy pooling entirely (PgBouncer already pools for us),
    # and statement_cache_size=0 disables prepared statements on asyncpg's
    # side - together these avoid DuplicatePreparedStatementError.
    _engine_kwargs["connect_args"] = {"ssl": "require", "statement_cache_size": 0}
    _engine_kwargs["poolclass"] = NullPool
else:
    _engine_kwargs["pool_pre_ping"] = True
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
    """Create all tables on startup. Fine for this project's scale; use Alembic migrations for larger schemas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
