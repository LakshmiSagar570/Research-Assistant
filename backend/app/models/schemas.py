"""
Pydantic schemas: the contract between frontend and backend.
Kept separate from ORM models so DB structure can evolve independently
of what we expose over the API.
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.orm import UserRole


# ---------- Auth / Users ----------

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.student
    college: str = Field(default="", max_length=255)
    department: str = Field(default="", max_length=255)


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    college: str = ""
    department: str = ""
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Papers / Search ----------

class PaperOut(BaseModel):
    id: str
    arxiv_id: str
    title: str
    abstract: str
    authors: str
    link: str
    source: str
    categories: str
    published: str
    summary: str
    added_date: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    max_results: int = Field(default=10, ge=1, le=30)


class SummarizeRequest(BaseModel):
    paper_id: str
    sentence_count: int = Field(default=4, ge=2, le=8)


# ---------- References ----------

class ReferenceCreate(BaseModel):
    paper_id: str


class ReferenceOut(BaseModel):
    id: str
    paper_id: str
    bibtex_entry: str
    apa_entry: str
    created_at: datetime
    paper: PaperOut

    class Config:
        from_attributes = True


# ---------- Gap Detection ----------

class GapDetectionRequest(BaseModel):
    paper_ids: list[str] = Field(min_length=2, max_length=50)


class GapCluster(BaseModel):
    keyword: str
    frequency: int
    coverage_ratio: float
    flag: str  # "under_represented" | "well_covered"


class GapDetectionResponse(BaseModel):
    total_papers_analyzed: int
    clusters: list[GapCluster]
    candidate_gaps: list[str]
    disclaimer: str = (
        "These are candidate gaps surfaced via keyword frequency analysis. "
        "They require human expert judgement before being treated as confirmed research gaps."
    )


# ---------- Review Generation ----------

class ReviewGenerateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    paper_ids: list[str] = Field(min_length=1, max_length=50)
    include_gap_analysis: bool = True


class ReviewOut(BaseModel):
    id: str
    title: str
    paper_ids: str
    content_markdown: str
    gaps_json: str
    export_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Research Projects ----------

class ResearchProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    description: str = Field(default="", max_length=2000)


class AddStudentRequest(BaseModel):
    student_email: EmailStr


class StudentOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    college: str = ""
    department: str = ""

    class Config:
        from_attributes = True


class ResearchProjectOut(BaseModel):
    id: str
    title: str
    description: str
    faculty_id: str
    faculty_name: str
    created_at: datetime
    members: list[StudentOut] = []

    class Config:
        from_attributes = True
