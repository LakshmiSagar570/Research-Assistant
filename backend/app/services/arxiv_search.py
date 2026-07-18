"""
FR1: Search papers via the arXiv API.

arXiv's API returns Atom XML; feedparser handles that cleanly without
us hand-rolling an XML parser. No API key required, which keeps this
in the "public API, zero subscription cost" scope the SRS commits to.
"""
import httpx
import feedparser
from urllib.parse import quote

from app.core.config import settings


class ArxivSearchError(Exception):
    pass


async def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    """
    Returns a list of dicts: arxiv_id, title, abstract, authors, link,
    categories, published. Raises ArxivSearchError on failure so the
    router can turn that into a graceful HTTP error (NFR: Reliability).
    """
    search_query = f"all:{quote(query)}"
    url = (
        f"{settings.ARXIV_API_URL}?search_query={search_query}"
        f"&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
    )

    try:
        async with httpx.AsyncClient(timeout=settings.ARXIV_TIMEOUT_SECONDS) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise ArxivSearchError(f"arXiv API request failed: {exc}") from exc

    feed = feedparser.parse(resp.text)
    if feed.bozo and not feed.entries:
        raise ArxivSearchError("arXiv API returned unparseable response")

    results = []
    for entry in feed.entries:
        arxiv_id = entry.get("id", "").split("/abs/")[-1]
        authors = ", ".join(a.get("name", "") for a in entry.get("authors", []))
        categories = ", ".join(t.get("term", "") for t in entry.get("tags", []))
        results.append({
            "arxiv_id": arxiv_id,
            "title": " ".join(entry.get("title", "").split()),  # collapse newlines/whitespace
            "abstract": " ".join(entry.get("summary", "").split()),
            "authors": authors,
            "link": entry.get("link", ""),
            "categories": categories,
            "published": entry.get("published", ""),
        })
    return results
