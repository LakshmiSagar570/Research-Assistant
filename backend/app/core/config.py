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

    # SQLite by default -> zero setup for grading/demo purposes.
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'app.db'}"

    # JWT
    JWT_SECRET: str = "change-this-secret-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours, convenient for demo sessions

    # arXiv
    ARXIV_API_URL: str = "https://export.arxiv.org/api/query"
    ARXIV_TIMEOUT_SECONDS: float = 8.0

    # Exported files (generated review .docx) land here
    EXPORTS_DIR: Path = BASE_DIR / "data" / "exports"

    # CORS - React/Vite dev server
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
    CORS_ORIGIN_REGEX: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

    class Config:
        env_file = ".env"


settings = Settings()
settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
