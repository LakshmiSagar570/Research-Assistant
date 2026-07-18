# AI Research Assistant

Full-stack implementation of the SRS: literature search, extractive summarization,
citation management, gap detection, and automated literature review generation.

Implements all 8 functional requirements (FR1–FR8) from the SRS.

## Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (async), SQLite (zero-setup local DB)
- **Frontend:** React 18 + TypeScript, Vite, React Router
- **Auth:** JWT (python-jose) + bcrypt password hashing, role-based access (student / faculty / admin)

No paid APIs are used anywhere — arXiv search is free and keyless, matching the SRS scope.

---

## 1. Backend setup (Windows PowerShell)

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend auto-creates the SQLite database (`app/data/app.db`) and seeds a demo account
on first startup:

```
email:    demo@college.edu
password: demo1234
role:     faculty
```

Visit `http://localhost:8000/docs` for interactive Swagger API docs — useful for demoing
each FR endpoint directly to a grader if needed.

### If PowerShell blocks the venv activation script

Run this once (as your normal user, not admin):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 2. Frontend setup (separate terminal)

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Sign in with the demo account above.

The frontend reads the backend URL from `frontend/.env` (`VITE_API_URL`), already set to
`http://localhost:8000`.

---

## 3. Demo walkthrough (for viva / grading)

1. **Sign in** with the demo account (FR7 — role: faculty).
2. **Search** — go to *Search*, query something like `dns tunneling detection`. Results are
   pulled live from arXiv (FR1).
3. **Summarize** — click *Summarize* on any result to generate an extractive summary (FR2).
4. **Save reference** — click *Save reference*; this generates BibTeX + APA citations (FR3)
   and stores it (FR4). Check the *References* page to see it, copy it, or export the whole
   library as `.bib`/`.txt` (FR8).
5. **Generate a review** — save at least 2–3 papers, go to *Reviews*, select them, give the
   review a title, and click *Generate review*. This runs gap detection (FR5) and builds a
   structured draft (FR6).
6. **Export** — on the review page, click *Export .docx* to download a real Word document
   (FR8). As a faculty/admin account you can also click *Approve*, demonstrating server-side
   role enforcement (FR7).

## Notes on scope and honesty (for the viva)

- **Gap detection (FR5)** is a frequency/thematic analysis over the selected paper set, not
  a semantic or citation-network method. It explicitly labels its output as "candidate gaps"
  requiring human judgement — this is intentional and documented in the SRS §15 Limitations.
- **Summarization (FR2)** is extractive (selects real sentences from the source), not
  abstractive/generative. This was a deliberate choice for zero cost, determinism, and zero
  hallucination risk — matching the SRS's "rule-based + extractive" architecture decision.
  Abstractive summarization via a local LLM (e.g. Ollama) is scoped as a future phase.
- Search is arXiv-only in this phase (SRS scope), so results outside arXiv's corpus (e.g.
  IEEE/Springer papers) will not appear.

## Project structure

```
backend/
  app/
    core/        # config, database, security, auth dependencies
    models/       # SQLAlchemy ORM models + Pydantic schemas
    routers/      # FastAPI route handlers (one per FR group)
    services/     # business logic: arxiv search, summarizer, citations,
                   # gap detection, review generation, docx export
    main.py       # app entrypoint
frontend/
  src/
    api/          # typed API client
    auth/         # auth context/provider
    components/   # shared UI (AppShell, buttons, cards)
    pages/        # one file per screen
```
