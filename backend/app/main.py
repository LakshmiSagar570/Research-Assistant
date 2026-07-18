"""
AI Research Assistant - FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload --port 8000

On startup this creates all tables (SQLite, zero-setup) and seeds a
single demo user so the app can be demoed immediately:
    email:    demo@college.edu
    password: demo1234
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.security import hash_password
from app.models.orm import User, UserRole
from app.routers import auth, papers, references, gaps, reviews


async def _seed_demo_user():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "demo@college.edu"))
        if result.scalar_one_or_none():
            return
        demo_user = User(
            name="Demo Faculty",
            email="demo@college.edu",
            password_hash=hash_password("demo1234"),
            role=UserRole.faculty,
        )
        db.add(demo_user)
        await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await _seed_demo_user()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Literature search, summarization, gap detection, and automated review generation.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(references.router)
app.include_router(gaps.router)
app.include_router(reviews.router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "demo_login": {"email": "demo@college.edu", "password": "demo1234"},
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
