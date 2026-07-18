"""
FR5: Detect candidate research gaps via thematic/frequency analysis.

Method (deliberately simple and explainable, per SRS scope §15
Limitations - this is NOT a semantic/citation-network gap analysis):

  1. Extract noun-like keyword candidates from each paper's abstract.
  2. Build a keyword -> paper-coverage map across the selected set.
  3. A keyword that appears in only a small fraction of papers, but
     appears meaningfully (>=1 strong mention) is flagged as an
     "under_represented" theme - a candidate gap worth a human look.
  4. A keyword appearing across most papers is "well_covered" - the
     opposite signal, useful for showing the method isn't just noise.

This is intentionally transparent: every score is traceable back to a
keyword count, so it can be explained line-by-line in a viva. It is
explicitly NOT presented as a definitive research-gap claim - see
GapDetectionResponse.disclaimer.
"""
import re
from collections import defaultdict
from app.models.orm import Paper
from app.models.schemas import GapCluster, GapDetectionResponse

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "for", "to", "with",
    "is", "are", "was", "were", "be", "been", "being", "this", "that", "these",
    "those", "we", "our", "it", "its", "as", "by", "at", "from", "which", "such",
    "can", "also", "into", "than", "then", "using", "used", "use", "based",
    "not", "no", "have", "has", "had", "will", "would", "may", "might", "their",
    "results", "paper", "study", "propose", "proposed", "show", "shows",
    "method", "methods", "approach", "approaches", "work", "novel", "new",
}

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-]{2,}")


def _keywords(text: str) -> set[str]:
    words = _WORD_RE.findall(text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 3}


def detect_gaps(papers: list[Paper]) -> GapDetectionResponse:
    total = len(papers)
    keyword_paper_count: dict[str, int] = defaultdict(int)
    keyword_total_mentions: dict[str, int] = defaultdict(int)

    for paper in papers:
        text = f"{paper.title} {paper.abstract}"
        words = _WORD_RE.findall(text.lower())
        words = [w for w in words if w not in _STOPWORDS and len(w) > 3]
        present = set(words)
        for kw in present:
            keyword_paper_count[kw] += 1
        for kw in words:
            keyword_total_mentions[kw] += 1

    single_paper_ratio = 1 / total if total else 0.0
    under_represented_ceiling = single_paper_ratio * 1.5
    well_covered_floor = 0.5 if total <= 4 else 0.6

    clusters: list[GapCluster] = []
    for kw, paper_count in keyword_paper_count.items():
        mentions = keyword_total_mentions[kw]
        if mentions < 2:
            continue
        coverage_ratio = paper_count / total if total else 0.0
        if total >= 3 and coverage_ratio <= under_represented_ceiling:
            flag = "under_represented"
        elif coverage_ratio >= well_covered_floor:
            flag = "well_covered"
        else:
            continue
        clusters.append(GapCluster(
            keyword=kw,
            frequency=mentions,
            coverage_ratio=round(coverage_ratio, 3),
            flag=flag,
        ))

    clusters.sort(key=lambda c: (c.flag != "under_represented", -c.frequency))
    clusters = clusters[:20]

    candidate_gaps = [
        f"'{c.keyword}' appears in only {round(c.coverage_ratio * 100)}% of the "
        f"selected papers ({c.frequency} mentions total) - potentially under-explored "
        f"within this paper set."
        for c in clusters if c.flag == "under_represented"
    ][:8]

    return GapDetectionResponse(
        total_papers_analyzed=total,
        clusters=clusters,
        candidate_gaps=candidate_gaps,
    )
