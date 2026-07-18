"""
FR3: Generate citations in BibTeX and APA format from a Paper record.
"""
import re
from app.models.orm import Paper


def _bibtex_key(paper: Paper) -> str:
    first_author_last = "unknown"
    if paper.authors:
        first_author = paper.authors.split(",")[0].strip()
        parts = first_author.split()
        if parts:
            first_author_last = re.sub(r"[^A-Za-z]", "", parts[-1]).lower() or "unknown"

    year = _extract_year(paper.published) or "n_d"
    first_word = re.sub(r"[^A-Za-z]", "", (paper.title.split()[0] if paper.title else "paper")).lower()
    return f"{first_author_last}{year}{first_word}"


def _extract_year(published: str) -> str:
    match = re.match(r"(\d{4})", published or "")
    return match.group(1) if match else ""


def to_bibtex(paper: Paper) -> str:
    key = _bibtex_key(paper)
    year = _extract_year(paper.published) or "n.d."
    authors_bibtex = " and ".join(a.strip() for a in (paper.authors or "").split(",") if a.strip())

    return (
        f"@article{{{key},\n"
        f"  title   = {{{paper.title}}},\n"
        f"  author  = {{{authors_bibtex}}},\n"
        f"  year    = {{{year}}},\n"
        f"  journal = {{arXiv preprint {paper.arxiv_id}}},\n"
        f"  url     = {{{paper.link}}}\n"
        f"}}"
    )


def _apa_authors(authors_csv: str) -> str:
    authors = [a.strip() for a in (authors_csv or "").split(",") if a.strip()]
    if not authors:
        return "Unknown Author"

    def to_apa_name(full_name: str) -> str:
        parts = full_name.split()
        if len(parts) < 2:
            return full_name
        last = parts[-1]
        initials = " ".join(f"{p[0]}." for p in parts[:-1])
        return f"{last}, {initials}"

    apa_names = [to_apa_name(a) for a in authors]
    if len(apa_names) == 1:
        return apa_names[0]
    if len(apa_names) <= 20:
        return ", ".join(apa_names[:-1]) + f", & {apa_names[-1]}"
    # APA 7th: 20+ authors -> first 19, ellipsis, last author
    return ", ".join(apa_names[:19]) + ", ... " + apa_names[-1]


def to_apa(paper: Paper) -> str:
    year = _extract_year(paper.published) or "n.d."
    authors = _apa_authors(paper.authors)
    return f"{authors} ({year}). {paper.title}. arXiv. {paper.link}"
