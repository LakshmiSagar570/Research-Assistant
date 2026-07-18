"""
FR1: Search papers via arXiv API.
FR2: Summarize abstracts.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.orm import User, Paper
from app.models.schemas import PaperOut, SearchRequest, SummarizeRequest
from app.services.arxiv_search import search_arxiv, ArxivSearchError
from app.services.summarizer import extractive_summary

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("/search", response_model=list[PaperOut])
async def search_papers(
    payload: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    FR1. Searches arXiv live, then upserts results into the local
    Papers table so they can be referenced (summarized, cited, added
    to a review) by ID afterward. Graceful degradation on API failure
    per NFR: Reliability.
    """
    try:
        raw_results = await search_arxiv(payload.query, payload.max_results)
    except ArxivSearchError as exc:
        raise HTTPException(status_code=503, detail=f"arXiv search unavailable: {exc}")

    if not raw_results:
        return []

    saved_papers: list[Paper] = []
    for r in raw_results:
        existing = await db.execute(select(Paper).where(Paper.arxiv_id == r["arxiv_id"]))
        paper = existing.scalar_one_or_none()
        if paper is None:
            paper = Paper(
                arxiv_id=r["arxiv_id"],
                title=r["title"],
                abstract=r["abstract"],
                authors=r["authors"],
                link=r["link"],
                categories=r["categories"],
                published=r["published"],
            )
            db.add(paper)
        saved_papers.append(paper)

    await db.commit()
    for p in saved_papers:
        await db.refresh(p)

    return saved_papers


@router.post("/summarize", response_model=PaperOut)
async def summarize_paper(
    payload: SummarizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR2. Computes (and caches) an extractive summary for a stored paper."""
    result = await db.execute(select(Paper).where(Paper.id == payload.paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper.summary = extractive_summary(paper.abstract, payload.sentence_count)
    await db.commit()
    await db.refresh(paper)
    return paper


@router.get("/{paper_id}", response_model=PaperOut)
async def get_paper(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("", response_model=list[PaperOut])
async def list_papers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Convenience endpoint: list all locally cached papers (e.g. for the review-selection UI)."""
    result = await db.execute(select(Paper).order_by(Paper.added_date.desc()))
    return result.scalars().all()
