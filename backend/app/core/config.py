"""
Central configuration for the AI Research Assistant backend.

All tunables live here so the rest of the codebase never hardcodes
secrets, paths, or magic numbers.
"""
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/app


class Settings(BaseSettings):
    APP_NAME: str = "AI Research Assistant"
    ENV: str = "development"

    # Local dev: SQLite (zero setup). Production: set DATABASE_URL to your
    # Supabase Postgres connection string (asyncpg driver) via environment
    # variable - never commit real prod credentials here.
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'app.db'}"

    # JWT - MUST be overridden via environment variable in production.
    # The default below is only safe for local/offline demo use.
    JWT_SECRET: str = "change-this-secret-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours, convenient for demo sessions

    # arXiv
    ARXIV_API_URL: str = "http://export.arxiv.org/api/query"
    ARXIV_TIMEOUT_SECONDS: float = 8.0

    # Exported files (generated review .docx) land here.
    # NOTE: on Vercel serverless, only /tmp is writable - see EXPORTS_DIR below.
    EXPORTS_DIR: Path = BASE_DIR / "data" / "exports"

    # CORS - comma-separated in production via env var, e.g.:
    # CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ]

    # Whether to seed the demo@college.edu account on startup. Defaults to
    # true for local dev convenience; MUST be false in production so no
    # publicly-known credential exists on the live deployment.
    SEED_DEMO_USER: bool = True

    # Rate limiting (requests per window) for auth endpoints, to slow down
    # credential-stuffing / brute-force attempts in production.
    LOGIN_RATE_LIMIT: str = "10/minute"
    REGISTER_RATE_LIMIT: str = "5/minute"

    class Config:
        env_file = ".env"

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"


settings = Settings()

if settings.is_production and settings.JWT_SECRET == "change-this-secret-in-production-please":
    raise RuntimeError(
        "JWT_SECRET is still set to the insecure default while ENV=production. "
        "Set a strong random JWT_SECRET environment variable before deploying."
    )

# On Vercel, only /tmp is writable at runtime; local filesystem elsewhere is
# read-only. Detect the serverless environment and redirect exports there.
if settings.is_production:
    settings.EXPORTS_DIR = Path("/tmp/exports")

settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
if not settings.is_production:
    (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
