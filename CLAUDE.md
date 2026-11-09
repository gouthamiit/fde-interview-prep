# CLAUDE.md — FDE Interview Prep Assistant

## What we're building
A small FastAPI app that runs mock Forward Deployed Engineer interviews and
scores the answers against a rubric. Favour **clarity over cleverness** — every
line should be explainable in an interview.

## Stack
- Python 3.11+, **FastAPI** (served by uvicorn), **Pydantic v2**
- Data: plain **JSON files** in `data/` — no database
- Scoring: an offline **mock** scorer, or the **OpenAI API** when a key is set
  (the model id lives in one constant, `app/config.MODEL_ID`)
- Tests: **pytest** — never call the network in a test
- Tooling: **ruff** (lint/format, rules E+F, line length 100), **mypy** (py3.11)

## Project layout
- `app/` — the FastAPI app: `main.py` (endpoints), `models.py` (Pydantic schemas),
  `scoring.py` (rubric scoring), `data.py` (all file I/O), `config.py` (settings)
- `data/` — `questions.json` (question bank), `rubric.md` (scoring rubric),
  `results.json` (saved scorecards; app-written, don't hand-edit)
- `resources/` — interview study guides (STAR, decomposition, system design);
  read-only reference material, served by the MCP server in Module 5
- `tests/` — pytest suite using FastAPI's `TestClient`

## Conventions
- Type-hint everything; keep functions small and named for what they do.
- Layering: endpoints in `main.py` stay thin → logic in `scoring.py` → disk
  access **only** in `data.py`. Nothing else opens files in `data/`.
- Every request/response body is a Pydantic model in `models.py`; endpoints
  declare their return type.
- All LLM prompts live as named constants in `scoring.py`, never inline.
- Config (model id, keys, paths) comes from `config.py` only — no
  `os.environ` lookups elsewhere, no hard-coded model ids.
- Errors: raise `HTTPException` with a clear `detail`; never leak a stack trace
  or raw upstream (OpenAI) error to the client.
- Rubric categories in `scoring.RUBRIC_CATEGORIES` must mirror `data/rubric.md`;
  change both together.
- Each module gets a short docstring explaining *why* it exists.
- Tests: no network — OpenAI calls are mocked/monkeypatched; the app must keep
  working with no `OPENAI_API_KEY` (mock scorer).

## Guardrails for you, the agent
- Show the plan before any multi-file or non-trivial change, and the diff
  before applying it.
- Work in small steps: one change → run → `pytest -q` → stop and report.
- When debugging, list and rank hypotheses **before** editing code; reproduce
  with a failing test first.
- When refactoring, don't change behaviour: tests stay green at every step.
- Don't "fix" the workshop's seeded bug / ugly function / stubs in `scoring.py`
  and `main.py` unless I ask — they're there on purpose.
- Never commit `.env`, API keys, or `data/results.json` contents; never print a
  key to the terminal.
- Don't add dependencies without asking; if approved, add them to
  `requirements.txt`.
- Never make real OpenAI calls from tests or ad-hoc scripts without asking
  first — they cost money.
- Run `ruff check .` and `mypy app` before saying a change is done.

## How to run
```
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload     # open http://127.0.0.1:8000/docs
pytest -q                         # tests (offline, free)
ruff check . && mypy app          # lint + type check
# Optional real scoring:  export OPENAI_API_KEY=sk-...  (OPENAI_MODEL overrides MODEL_ID)
```
