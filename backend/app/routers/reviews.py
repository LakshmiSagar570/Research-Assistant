"""
FR6: Generate literature review document.
FR8: Export references and reviews.
Also implements the Faculty-only "approve shared review" permission
from the SRS User Roles section.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.orm import User, Paper, Review, UserRole
from app.models.schemas import ReviewGenerateRequest, ReviewOut
from app.services.gap_detection import detect_gaps
from app.services.review_generator import generate_review_markdown
from app.services.review_export import markdown_to_docx_bytes
from app.services.summarizer import extractive_summary

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/generate", response_model=ReviewOut, status_code=201)
async def generate_review(
    payload: ReviewGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR6: builds a structured review draft from the selected papers."""
    result = await db.execute(select(Paper).where(Paper.id.in_(payload.paper_ids)))
    papers = result.scalars().all()

    if not papers:
        raise HTTPException(status_code=404, detail="No matching papers found")

    changed = False
    for p in papers:
        if not p.summary:
            p.summary = extractive_summary(p.abstract, 4)
            changed = True
    if changed:
        await db.commit()

    gaps = None
    if payload.include_gap_analysis and len(papers) >= 2:
        gaps = detect_gaps(papers)

    markdown = generate_review_markdown(payload.title, papers, gaps)

    review = Review(
        user_id=current_user.id,
        title=payload.title,
        paper_ids=",".join(p.id for p in papers),
        content_markdown=markdown,
        gaps_json=json.dumps(gaps.model_dump()) if gaps else "[]",
        status="draft",
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("", response_model=list[ReviewOut])
async def list_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Review).where(Review.user_id == current_user.id).order_by(Review.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{review_id}/download")
async def download_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    FR8: renders the review's Markdown into a .docx and streams it back
    in this same request. Also marks the review as exported. Combining
    generation and download into one request avoids relying on a file
    written to disk in an earlier request being readable later - see
    services/review_export.py for why that matters on serverless hosts.
    """
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    docx_bytes = markdown_to_docx_bytes(review.content_markdown)

    review.export_path = "generated"  # marker only; the file itself is not persisted server-side
    await db.commit()

    filename = f"{review.title.replace(' ', '_')}.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{review_id}/approve", response_model=ReviewOut)
async def approve_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.faculty, UserRole.admin)),
):
    """
    Faculty/Admin-only: 'approve shared reviews' per SRS User Roles
    section. Demonstrates server-side role enforcement (FR7).
    """
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.status = "approved"
    await db.commit()
    await db.refresh(review)
    return review

    review.status = "approved"
    await db.commit()
    await db.refresh(review)
    return review
