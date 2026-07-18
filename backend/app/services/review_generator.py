"""
FR6: Generate a structured literature review draft from selected papers.

Structure produced (matches SRS Review Generator flow: Select -> Generate
-> Preview -> Export):
  1. Introduction (auto-composed from paper count + topic keywords)
  2. Thematic grouping of papers (grouped by dominant arXiv category)
  3. Per-paper synthesis paragraph (built from cached extractive summary)
  4. Candidate research gaps section (optional, from gap_detection)
  5. References section (APA)

Output is Markdown (content_markdown) for easy preview in the frontend,
and is also rendered to .docx for FR8 export via review_export.py.
"""
from collections import defaultdict
from app.models.orm import Paper
from app.models.schemas import GapDetectionResponse
from app.services.citations import to_apa


def _primary_category(categories_csv: str) -> str:
    cats = [c.strip() for c in (categories_csv or "").split(",") if c.strip()]
    return cats[0] if cats else "Uncategorized"


def generate_review_markdown(
    title: str,
    papers: list[Paper],
    gaps: GapDetectionResponse | None = None,
) -> str:
    lines: list[str] = []
    lines.append(f"# {title}\n")

    # --- Introduction ---
    lines.append("## 1. Introduction\n")
    lines.append(
        f"This literature review synthesizes **{len(papers)} papers** retrieved from arXiv, "
        f"covering the selected research area. Papers are grouped thematically below by their "
        f"primary subject category, with a synthesis of each paper's core contribution followed "
        f"by candidate research gaps identified through frequency-based thematic analysis.\n"
    )

    # --- Thematic grouping ---
    groups: dict[str, list[Paper]] = defaultdict(list)
    for p in papers:
        groups[_primary_category(p.categories)].append(p)

    lines.append("## 2. Thematic Overview\n")
    for category, group_papers in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"### 2.{list(groups.keys()).index(category) + 1} {category} ({len(group_papers)} paper(s))\n")
        for p in group_papers:
            summary_text = p.summary or p.abstract[:280]
            authors_short = p.authors.split(",")[0].strip() + (" et al." if "," in p.authors else "")
            lines.append(f"**{p.title}** ({authors_short}). {summary_text}\n")

    # --- Gaps ---
    if gaps and gaps.candidate_gaps:
        lines.append("## 3. Candidate Research Gaps\n")
        lines.append(f"*{gaps.disclaimer}*\n")
        for gap in gaps.candidate_gaps:
            lines.append(f"- {gap}")
        lines.append("")

    # --- References ---
    section_num = 4 if gaps and gaps.candidate_gaps else 3
    lines.append(f"## {section_num}. References\n")
    for p in sorted(papers, key=lambda x: x.title):
        lines.append(f"- {to_apa(p)}")

    return "\n".join(lines)
