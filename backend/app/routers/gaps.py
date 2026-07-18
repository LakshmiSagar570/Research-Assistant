"""
FR5: Detect research gaps.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.orm import User, Paper
from app.models.schemas import GapDetectionRequest, GapDetectionResponse
from app.services.gap_detection import detect_gaps

router = APIRouter(prefix="/gaps", tags=["gap-detection"])


@router.post("/detect", response_model=GapDetectionResponse)
async def detect_research_gaps(
    payload: GapDetectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Paper).where(Paper.id.in_(payload.paper_ids)))
    papers = result.scalars().all()

    if len(papers) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 valid papers are required for gap analysis",
        )

    return detect_gaps(papers)
