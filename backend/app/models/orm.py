"""
ORM models mirroring the SRS Database Design section:
  Papers, Users, References, Reviews.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    student = "student"
    faculty = "faculty"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.student)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    references: Mapped[list["Reference"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    arxiv_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str] = mapped_column(Text)
    authors: Mapped[str] = mapped_column(Text)  # comma-separated
    link: Mapped[str] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(50), default="arxiv")
    categories: Mapped[str] = mapped_column(Text, default="")  # comma-separated arXiv categories
    published: Mapped[str] = mapped_column(String(40), default="")
    summary: Mapped[str] = mapped_column(Text, default="")  # cached extractive summary
    added_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Reference(Base):
    __tablename__ = "references_table"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    paper_id: Mapped[str] = mapped_column(String(36), ForeignKey("papers.id"))
    bibtex_entry: Mapped[str] = mapped_column(Text)
    apa_entry: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    owner: Mapped["User"] = relationship(back_populates="references")
    paper: Mapped["Paper"] = relationship()


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(300))
    paper_ids: Mapped[str] = mapped_column(Text)  # comma-separated Paper.id list
    content_markdown: Mapped[str] = mapped_column(Text)
    gaps_json: Mapped[str] = mapped_column(Text, default="[]")
    export_path: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft | approved
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    owner: Mapped["User"] = relationship(back_populates="reviews")
