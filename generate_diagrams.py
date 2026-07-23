#!/usr/bin/env python3
"""
Generates 5 publication-grade Chapter 4 diagrams for the AI Research Assistant project report.

OUTPUT:
    ./diagrams_out/fig4_1_architecture.png
    ./diagrams_out/fig4_2_er_diagram.png
    ./diagrams_out/fig4_3_dfd_level0.png
    ./diagrams_out/fig4_4_dfd_level1.png
    ./diagrams_out/fig4_5_uml_usecase.png
"""

import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse

OUT_DIR = "./diagrams_out"
os.makedirs(OUT_DIR, exist_ok=True)

DPI = 300  # High DPI for sharp, professional rendering

COLORS = {
    "blue_fill":   "#EBF3FA", "blue_edge":   "#1B65A6", "blue_text":   "#0D3C68",
    "purple_fill": "#F0EEFB", "purple_edge": "#5A4FB8", "purple_text": "#372E7B",
    "teal_fill":   "#E6F6F2", "teal_edge":   "#0F7A60", "teal_text":   "#094A3B",
    "coral_fill":  "#FDF0EC", "coral_edge":  "#AA4523", "coral_text":  "#6D2B14",
    "pink_fill":   "#FCECF2", "pink_edge":   "#AA3960", "pink_text":   "#6E203B",
    "gray_fill":   "#F4F3EF", "gray_edge":   "#555450", "gray_text":   "#222220",
    "line":        "#333333",
}


def new_figure(width, height):
    """Creates a figure with exact data coordinates (0..width, 0..height)."""
    fig, ax = plt.subplots(figsize=(width / 72, height / 72), dpi=DPI)
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")
    ax.set_aspect("equal")
    return fig, ax


def draw_box(ax, x, y, w, h, title, subtitle=None, fill="#EBF3FA", edge="#1B65A6",
             title_color="#0D3C68", subtitle_color="#1B65A6", fontsize=11, sub_fontsize=8.5):
    """Draws rounded rectangle box with crisp centered text."""
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=8",
        linewidth=1.3, edgecolor=edge, facecolor=fill, zorder=2
    )
    ax.add_patch(patch)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=title_color, zorder=3)
        ax.text(x + w / 2, y + h * 0.31, subtitle, ha="center", va="center",
                fontsize=sub_fontsize, color=subtitle_color, zorder=3)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=title_color, zorder=3)


def draw_arrow(ax, start, end, label=None, label_pos=None, dashed=False, color="#333333",
               has_head=True, arrowstyle="->,head_width=0.35,head_length=0.5", fontsize=8.5):
    """Draws explicit straight data-coordinate arrow/line with white-background label card."""
    linestyle = "dashed" if dashed else "solid"
    
    if has_head:
        arrowprops = dict(
            arrowstyle=arrowstyle,
            linewidth=1.2, color=color, linestyle=linestyle
        )
        ax.annotate("", xy=end, xytext=start, xycoords="data", textcoords="data",
                    arrowprops=arrowprops, zorder=3)
    else:
        ax.plot([start[0], end[0]], [start[1], end[1]], color=color,
                linewidth=1.2, linestyle=linestyle, zorder=3)

    if label:
        lx, ly = label_pos if label_pos else ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        ax.text(lx, ly, label, fontsize=fontsize, color="#222222", fontweight="bold" if dashed else "normal",
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#CCCCCC", linewidth=0.6, alpha=0.95),
                zorder=5)


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.15, facecolor="white")
    plt.close(fig)
    print("saved:", path)


# ---------------------------------------------------------------------------
# Fig 4.1 - System Architecture
# ---------------------------------------------------------------------------
def draw_architecture():
    W, H = 800, 500
    fig, ax = new_figure(W, H)

    # Component boxes
    draw_box(ax, 280, 410, 240, 60, "Frontend Client", "React 18, TypeScript, Vite",
             COLORS["blue_fill"], COLORS["blue_edge"], COLORS["blue_text"], COLORS["blue_text"])

    draw_box(ax, 280, 285, 240, 60, "Backend API Layer", "FastAPI (async), SQLAlchemy ORM",
             COLORS["purple_fill"], COLORS["purple_edge"], COLORS["purple_text"], COLORS["purple_text"])

    draw_box(ax, 80, 160, 260, 65, "Database Persistence", "SQLite (Local) / Supabase Postgres (Prod)",
             COLORS["teal_fill"], COLORS["teal_edge"], COLORS["teal_text"], COLORS["teal_text"])

    draw_box(ax, 460, 160, 260, 65, "arXiv API Service", "External Paper & Metadata Search",
             COLORS["coral_fill"], COLORS["coral_edge"], COLORS["coral_text"], COLORS["coral_text"])

    draw_box(ax, 150, 30, 500, 75, "Deployment & Infrastructure",
             "Vercel (Frontend & Serverless API via Mangum)\nSupabase (Managed Database) | Zero Paid API Dependencies",
             COLORS["gray_fill"], COLORS["gray_edge"], COLORS["gray_text"], COLORS["gray_text"])

    # Arrows
    draw_arrow(ax, (400, 410), (400, 345), label="REST API (HTTPS + JWT)")
    draw_arrow(ax, (310, 285), (210, 225), label="Async ORM Queries")
    draw_arrow(ax, (490, 285), (590, 225), label="HTTP Search Request")
    draw_arrow(ax, (210, 160), (210, 105), dashed=True, label="Hosted DB")
    draw_arrow(ax, (590, 160), (590, 105), dashed=True, label="Free arXiv Service")

    save(fig, "fig4_1_architecture.png")


# ---------------------------------------------------------------------------
# Fig 4.2 - Entity-Relationship Diagram
# ---------------------------------------------------------------------------
def er_entity(ax, x, y, w, h, title, fields, fill, edge, header_text_color="white"):
    box_patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6",
                                linewidth=1.3, edgecolor=edge, facecolor=fill, zorder=2)
    ax.add_patch(box_patch)
    header_h = 28
    header = FancyBboxPatch((x, y + h - header_h), w, header_h, boxstyle="round,pad=0,rounding_size=6",
                             linewidth=0, facecolor=edge, zorder=3)
    ax.add_patch(header)
    ax.text(x + w / 2, y + h - 14, title, ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=header_text_color, zorder=4)

    line_y = y + h - header_h - 14
    for field in fields:
        ax.text(x + 12, line_y, field, fontsize=9, color="#222222", va="center", zorder=4)
        line_y -= 18


def draw_er():
    W, H = 840, 520
    fig, ax = new_figure(W, H)

    er_entity(ax, 40, 330, 220, 140, "User",
              ["PK  id  (INT)", "     email  (VARCHAR)", "     password_hash  (VARCHAR)", "     role  (ENUM)", "     created_at  (DATETIME)"],
              COLORS["blue_fill"], COLORS["blue_edge"])

    er_entity(ax, 320, 320, 220, 160, "Paper",
              ["PK  id  (INT)", "FK  saved_by  (User.id)", "     arxiv_id  (VARCHAR)", "     title  (TEXT)", "     authors  (TEXT)", "     abstract  (TEXT)", "     created_at  (DATETIME)"],
              COLORS["purple_fill"], COLORS["purple_edge"])

    er_entity(ax, 600, 330, 200, 140, "Citation",
              ["PK  id  (INT)", "FK  paper_id  (Paper.id)", "     bibtex  (TEXT)", "     apa  (TEXT)", "     created_at  (DATETIME)"],
              COLORS["teal_fill"], COLORS["teal_edge"])

    er_entity(ax, 160, 60, 220, 160, "Review",
              ["PK  id  (INT)", "FK  user_id  (User.id)", "     title  (VARCHAR)", "     content  (TEXT)", "     status  (VARCHAR)", "     created_at  (DATETIME)"],
              COLORS["coral_fill"], COLORS["coral_edge"])

    er_entity(ax, 520, 60, 260, 160, "ResearchProject",
              ["PK  id  (VARCHAR)", "FK  faculty_id  (User.id)", "     title  (VARCHAR)", "     description  (TEXT)", "     created_at  (DATETIME)"],
              COLORS["blue_fill"], COLORS["blue_edge"])

    # Relationships
    draw_arrow(ax, (260, 400), (320, 400), label="1 : N  (saves)")
    draw_arrow(ax, (540, 400), (600, 400), label="1 : 1  (generates)")
    draw_arrow(ax, (150, 330), (220, 220), label="1 : N  (writes)")
    draw_arrow(ax, (340, 220), (430, 320), label="N : M  (references)", dashed=True)
    draw_arrow(ax, (150, 330), (520, 140), label="1 : N  (leads & pulls students)")

    save(fig, "fig4_2_er_diagram.png")


# ---------------------------------------------------------------------------
# Fig 4.3 - DFD Level 0 (Context Diagram)
# ---------------------------------------------------------------------------
def draw_dfd_level0():
    W, H = 800, 420
    fig, ax = new_figure(W, H)

    # Process circle
    circle = Circle((400, 210), 90, facecolor=COLORS["purple_fill"],
                    edgecolor=COLORS["purple_edge"], linewidth=1.4, zorder=2)
    ax.add_patch(circle)
    ax.text(400, 225, "0. AI Research", ha="center", va="center",
            fontsize=13, fontweight="bold", color=COLORS["purple_text"], zorder=3)
    ax.text(400, 195, "Assistant System", ha="center", va="center",
            fontsize=13, fontweight="bold", color=COLORS["purple_text"], zorder=3)

    # External Entities
    draw_box(ax, 40, 175, 160, 70, "User", "Student / Faculty",
             COLORS["gray_fill"], COLORS["gray_edge"], COLORS["gray_text"], COLORS["gray_text"],
             fontsize=12, sub_fontsize=8.5)

    draw_box(ax, 600, 175, 160, 70, "arXiv API", "External Paper Source",
             COLORS["gray_fill"], COLORS["gray_edge"], COLORS["gray_text"], COLORS["gray_text"],
             fontsize=12, sub_fontsize=8.5)

    # Data flows
    draw_arrow(ax, (200, 225), (313, 225), label="Search queries, credentials, paper selections", label_pos=(256, 245))
    draw_arrow(ax, (313, 195), (200, 195), label="Summaries, citations, generated reviews, DOCX", label_pos=(256, 175))

    draw_arrow(ax, (487, 225), (600, 225), label="Search request (keywords / topics)", label_pos=(544, 245))
    draw_arrow(ax, (600, 195), (487, 195), label="Paper metadata & abstracts", label_pos=(544, 175))

    ax.text(400, 30, "DFD Level 0 - High-level system context diagram showing inputs & outputs with external entities.",
            ha="center", va="center", fontsize=9.5, color="#555555")

    save(fig, "fig4_3_dfd_level0.png")


# ---------------------------------------------------------------------------
# Fig 4.4 - DFD Level 1
# ---------------------------------------------------------------------------
def draw_dfd_level1():
    W, H = 920, 600
    fig, ax = new_figure(W, H)

    # External entities (top row)
    draw_box(ax, 60, 510, 150, 55, "User", fill=COLORS["gray_fill"], edge=COLORS["gray_edge"],
             title_color=COLORS["gray_text"], fontsize=11)
    draw_box(ax, 710, 510, 150, 55, "arXiv API", fill=COLORS["gray_fill"], edge=COLORS["gray_edge"],
             title_color=COLORS["gray_text"], fontsize=11)

    # Process circles (r=48)
    p1 = (160, 370)  # 1.0 Auth
    p2 = (440, 370)  # 2.0 Search
    p3 = (720, 370)  # 3.0 Summarize & Cite
    p4 = (440, 200)  # 4.0 Review Gen & Export
    r = 48

    processes = [
        (p1, "1.0 Auth", "JWT & Roles", COLORS["blue_fill"], COLORS["blue_edge"], COLORS["blue_text"]),
        (p2, "2.0 Search", "arXiv Fetch", COLORS["purple_fill"], COLORS["purple_edge"], COLORS["purple_text"]),
        (p3, "3.0 Summarize", "& Cite", COLORS["teal_fill"], COLORS["teal_edge"], COLORS["teal_text"]),
        (p4, "4.0 Review", "Gen & Export", COLORS["coral_fill"], COLORS["coral_edge"], COLORS["coral_text"]),
    ]

    for (cx, cy), title1, title2, fill, edge, tcolor in processes:
        ax.add_patch(Circle((cx, cy), r, facecolor=fill, edgecolor=edge, linewidth=1.3, zorder=2))
        ax.text(cx, cy + 8, title1, ha="center", va="center", fontsize=10.5, fontweight="bold", color=tcolor, zorder=3)
        ax.text(cx, cy - 8, title2, ha="center", va="center", fontsize=10.5, fontweight="bold", color=tcolor, zorder=3)

    # Data Store D1 (Bottom row)
    ax.plot([80, 840], [95, 95], color=COLORS["gray_edge"], linewidth=1.4, zorder=2)
    ax.plot([80, 840], [40, 40], color=COLORS["gray_edge"], linewidth=1.4, zorder=2)
    ax.text(100, 67.5, "D1: Database (Users, Saved Papers, Citations, Reviews)",
            fontsize=11, fontweight="bold", color=COLORS["gray_text"], va="center", zorder=3)

    # Main Process Flows
    draw_arrow(ax, (135, 510), (160, 418), label="Credentials")
    draw_arrow(ax, (208, 370), (392, 370), label="Auth Token")
    draw_arrow(ax, (474, 404), (730, 510), label="Search Query")
    draw_arrow(ax, (760, 510), (754, 404), label="Paper Metadata")
    draw_arrow(ax, (488, 370), (672, 370), label="Paper Text")
    draw_arrow(ax, (720, 322), (488, 200), label="Summaries & Citations")
    draw_arrow(ax, (440, 322), (440, 248), label="Saved Papers")

    # Clean return flow from Process 4.0 routed up through clear central space to User box
    draw_arrow(ax, (392, 200), (290, 200), has_head=False)
    draw_arrow(ax, (290, 200), (290, 465), has_head=False)
    draw_arrow(ax, (290, 465), (210, 520), label="Review & DOCX Export", label_pos=(290, 310))

    # Database Store Flows (vertical dashed arrows straight down to D1)
    draw_arrow(ax, (160, 322), (160, 95), label="User Records", dashed=True, label_pos=(160, 140))
    draw_arrow(ax, (440, 152), (440, 95), label="Reviews & Gaps", dashed=True, label_pos=(440, 128))
    draw_arrow(ax, (720, 322), (720, 95), label="Citations", dashed=True, label_pos=(720, 140))

    save(fig, "fig4_4_dfd_level1.png")


# ---------------------------------------------------------------------------
# Fig 4.5 - Pristine Publication-Grade UML Use Case Diagram
# ---------------------------------------------------------------------------
def stick_actor(ax, x, y, label, scale=1.0):
    """Draws stick actor figure with label positioned neatly below legs."""
    head_r = 14 * scale
    ax.add_patch(Circle((x, y), head_r, facecolor="white", edgecolor=COLORS["gray_text"], linewidth=1.6, zorder=3))
    body_top = y - head_r
    body_bottom = body_top - 40 * scale
    ax.plot([x, x], [body_top, body_bottom], color=COLORS["gray_text"], linewidth=1.6, zorder=3)
    arm_y = body_top - 14 * scale
    ax.plot([x - 20 * scale, x + 20 * scale], [arm_y, arm_y], color=COLORS["gray_text"], linewidth=1.6, zorder=3)
    ax.plot([x, x - 18 * scale], [body_bottom, body_bottom - 32 * scale], color=COLORS["gray_text"], linewidth=1.6, zorder=3)
    ax.plot([x, x + 18 * scale], [body_bottom, body_bottom - 32 * scale], color=COLORS["gray_text"], linewidth=1.6, zorder=3)
    ax.text(x, body_bottom - 46 * scale, label, ha="center", va="center",
            fontsize=12, fontweight="bold", color=COLORS["gray_text"], zorder=3)


def use_case_ellipse(ax, cx, cy, rx, ry, label, fill, edge, tcolor, fontsize=9.5):
    ax.add_patch(Ellipse((cx, cy), rx * 2, ry * 2, facecolor=fill, edgecolor=edge, linewidth=1.3, zorder=2))
    ax.text(cx, cy, label, ha="center", va="center", fontsize=fontsize, fontweight="bold", color=tcolor, zorder=3)


def draw_uml_usecase():
    W, H = 960, 640
    fig, ax = new_figure(W, H)

    # System boundary box with title centered outside top margin
    boundary = FancyBboxPatch((200, 30), 560, 560, boxstyle="round,pad=0,rounding_size=8",
                               linewidth=1.3, edgecolor=COLORS["gray_edge"], facecolor="none",
                               linestyle="dashed", zorder=1)
    ax.add_patch(boundary)
    ax.text(480, 565, "AI Research Assistant System", ha="center", va="center",
            fontsize=14, fontweight="bold", color=COLORS["gray_text"], zorder=3)

    # Actors: Student on Left, Faculty on Right
    stick_actor(ax, 85, 310, "Student")
    stick_actor(ax, 875, 180, "Faculty")

    # Left Column Use Cases (x=350) - Student workflow
    uc_login      = (350, 520, 85, 22, "Register / Login", COLORS["blue_fill"], COLORS["blue_edge"], COLORS["blue_text"])
    uc_search     = (350, 440, 85, 22, "Search Papers", COLORS["purple_fill"], COLORS["purple_edge"], COLORS["purple_text"])
    uc_summarize  = (350, 360, 85, 22, "Summarize & Cite", COLORS["teal_fill"], COLORS["teal_edge"], COLORS["teal_text"])
    uc_manage_ref = (350, 280, 85, 22, "Manage References", COLORS["teal_fill"], COLORS["teal_edge"], COLORS["teal_text"])
    uc_review     = (350, 200, 95, 22, "Generate Review & Gaps", COLORS["coral_fill"], COLORS["coral_edge"], COLORS["coral_text"])
    uc_export     = (350, 110, 85, 22, "Export DOCX", COLORS["pink_fill"], COLORS["pink_edge"], COLORS["pink_text"])

    # Right Column Use Cases (x=630) - Faculty features
    uc_approve    = (630, 200, 85, 22, "Approve Review", COLORS["coral_fill"], COLORS["coral_edge"], COLORS["coral_text"])
    uc_pull       = (630, 110, 95, 22, "Pull Students to Research", COLORS["blue_fill"], COLORS["blue_edge"], COLORS["blue_text"])

    all_usecases = [uc_login, uc_search, uc_summarize, uc_manage_ref, uc_review, uc_export, uc_approve, uc_pull]
    for uc in all_usecases:
        use_case_ellipse(ax, *uc)

    # Student Associations (origin from Student center torso (85, 310) -> left perimeters)
    draw_arrow(ax, (85, 310), (265, 520), has_head=False)  # Register / Login
    draw_arrow(ax, (85, 310), (265, 440), has_head=False)  # Search Papers
    draw_arrow(ax, (85, 310), (265, 360), has_head=False)  # Summarize & Cite
    draw_arrow(ax, (85, 310), (265, 280), has_head=False)  # Manage References
    draw_arrow(ax, (85, 310), (255, 200), has_head=False)  # Generate Review & Gaps
    draw_arrow(ax, (85, 310), (265, 110), has_head=False)  # Export DOCX

    # Faculty Associations (origin from Faculty center torso (875, 180) -> right perimeters)
    draw_arrow(ax, (875, 180), (725, 110), has_head=False)  # Pull Students to Research
    draw_arrow(ax, (875, 180), (715, 200), has_head=False)  # Approve Review
    draw_arrow(ax, (875, 180), (435, 440), has_head=False)  # Search Papers (Passes 131px above Approve Review)

    # Dashed Includes (Clean straight arrows with non-overlapping label cards)
    draw_arrow(ax, (445, 200), (545, 200), label="<<include>>", dashed=True)  # Review -> Approve (100% Horizontal!)
    draw_arrow(ax, (350, 178), (350, 132), label="<<include>>", dashed=True)  # Review -> Export DOCX (100% Vertical!)

    save(fig, "fig4_5_uml_usecase.png")


if __name__ == "__main__":
    draw_architecture()
    draw_er()
    draw_dfd_level0()
    draw_dfd_level1()
    draw_uml_usecase()
    print("\nAll 5 diagrams successfully generated in:", os.path.abspath(OUT_DIR))
