"""
FR8: Export generated literature reviews as .docx.

Takes the Markdown produced by review_generator.py and renders it into
a real Word document using python-docx, matching the SRS tech stack
("Document Generation: python-docx").

This is a small, deliberately simple Markdown -> docx renderer: it only
needs to handle the subset of Markdown that generate_review_markdown()
actually produces (#/##/### headings, **bold**, "- " bullets, plain
paragraphs). It is not a general-purpose Markdown parser.
"""
import re
import uuid
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.core.config import settings

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _add_paragraph_with_bold(doc: Document, text: str, style: str | None = None):
    p = doc.add_paragraph(style=style)
    pos = 0
    for match in _BOLD_RE.finditer(text):
        if match.start() > pos:
            p.add_run(text[pos:match.start()])
        run = p.add_run(match.group(1))
        run.bold = True
        pos = match.end()
    if pos < len(text):
        p.add_run(text[pos:])
    return p


def markdown_to_docx(markdown_text: str, review_id: str) -> str:
    doc = Document()

    # Base font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    for raw_line in markdown_text.split("\n"):
        line = raw_line.rstrip()
        if not line:
            continue

        if line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            h = doc.add_heading(line[2:], level=1)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith("*") and line.endswith("*") and not line.startswith("**"):
            p = doc.add_paragraph()
            run = p.add_run(line.strip("*"))
            run.italic = True
        elif line.startswith("- "):
            _add_paragraph_with_bold(doc, line[2:], style="List Bullet")
        else:
            _add_paragraph_with_bold(doc, line)

    filename = f"review_{review_id}_{uuid.uuid4().hex[:8]}.docx"
    out_path = Path(settings.EXPORTS_DIR) / filename
    doc.save(str(out_path))
    return str(out_path)
