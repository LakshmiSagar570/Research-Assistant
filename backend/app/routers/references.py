"""
FR3: Generate citations (APA/BibTeX).
FR4: Add/manage references in local database.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.orm import User, Paper, Reference
from app.models.schemas import ReferenceCreate, ReferenceOut
from app.services.citations import to_bibtex, to_apa

router = APIRouter(prefix="/references", tags=["references"])


@router.post("", response_model=ReferenceOut, status_code=201)
async def add_reference(
    payload: ReferenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR3 + FR4: generates citations for a paper and saves it to the user's reference library."""
    result = await db.execute(select(Paper).where(Paper.id == payload.paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    existing = await db.execute(
        select(Reference).where(
            Reference.user_id == current_user.id, Reference.paper_id == paper.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Reference already saved")

    reference = Reference(
        user_id=current_user.id,
        paper_id=paper.id,
        bibtex_entry=to_bibtex(paper),
        apa_entry=to_apa(paper),
    )
    db.add(reference)
    await db.commit()

    result = await db.execute(
        select(Reference)
        .options(selectinload(Reference.paper))
        .where(Reference.id == reference.id)
    )
    return result.scalar_one()


@router.get("", response_model=list[ReferenceOut])
async def list_references(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR4: list the current user's saved references."""
    result = await db.execute(
        select(Reference)
        .options(selectinload(Reference.paper))
        .where(Reference.user_id == current_user.id)
        .order_by(Reference.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{reference_id}", status_code=204)
async def delete_reference(
    reference_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR4: remove a reference from the user's library."""
    result = await db.execute(
        select(Reference).where(
            Reference.id == reference_id, Reference.user_id == current_user.id
        )
    )
    reference = result.scalar_one_or_none()
    if not reference:
        raise HTTPException(status_code=404, detail="Reference not found")

    await db.delete(reference)
    await db.commit()
    return None
