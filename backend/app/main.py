"""
AI Research Assistant - FastAPI application entry point.

Local dev:
    uvicorn app.main:app --reload --port 8000
    -> creates SQLite tables and seeds demo@college.edu / demo1234

Production (ENV=production):
    -> connects to DATABASE_URL (Supabase Postgres), does NOT seed the
       demo account, enforces a real JWT_SECRET, and applies rate
       limiting + security headers.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.security import hash_password
from app.core.limiter import limiter
from app.models.orm import User, UserRole
from app.routers import auth, papers, references, gaps, reviews, projects


async def _seed_demo_user():
    """Only ever runs when SEED_DEMO_USER=true (local/dev default). In
    production this is disabled so no publicly-documented credential
    exists on the live deployment - see core/config.py."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "demo@college.edu"))
        if not result.scalar_one_or_none():
            demo_user = User(
                name="Demo Faculty",
                email="demo@college.edu",
                password_hash=hash_password("demo1234"),
                role=UserRole.faculty,
            )
            db.add(demo_user)

        s_result = await db.execute(select(User).where(User.email == "student@college.edu"))
        if not s_result.scalar_one_or_none():
            student_user = User(
                name="Alex Student",
                email="student@college.edu",
                password_hash=hash_password("student1234"),
                role=UserRole.student,
            )
            db.add(student_user)

        await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if settings.SEED_DEMO_USER and not settings.is_production:
        await _seed_demo_user()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Literature search, summarization, gap detection, and automated review generation.",
    version="2.0.0",
    lifespan=lifespan,
    # Hide interactive API docs in production - they're a convenience for
    # grading/dev, not something a public deployment should expose.
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Baseline security headers. Not a substitute for HTTPS termination
    (Vercel provides that at the edge) but closes off common client-side
    injection/sniffing vectors."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(references.router)
app.include_router(gaps.router)
app.include_router(reviews.router)
app.include_router(projects.router)


@app.get("/")
async def root():
    payload = {
        "app": settings.APP_NAME,
        "status": "running",
        "docs": "/docs" if not settings.is_production else None,
    }
    if not settings.is_production:
        payload["demo_login"] = {"email": "demo@college.edu", "password": "demo1234"}
    return payload


@app.get("/health")
async def health():
    return {"status": "ok"}
