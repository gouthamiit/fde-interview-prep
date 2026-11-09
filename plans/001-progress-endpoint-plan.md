# Plan: GET /progress

## Context
Add a read-only endpoint that summarises practice history from `data/results.json`:
how many rounds have been practised and the average total score. Today the file is
`[]` and **nothing writes to it yet** (`data.save_result()` exists but `/score` is
still a stub), so this endpoint also implicitly defines the record shape `/score`
must save later.

Definitions (recommended):
- `rounds_practised` = number of saved results (attempts), not distinct round types.
- `average_total` = mean of each record's `total`, rounded to 1 dp; `null` when empty.

## 1. Files and changes
- **`app/models.py`** — add `ProgressResponse(BaseModel)`: `rounds_practised: int`,
  `average_total: float | None`.
- **`app/data.py`** — add `load_results() -> list[dict]`: reads `DATA_DIR / "results.json"`;
  returns `[]` if the file is missing. (Disk access stays only in `data.py`.)
- **`app/progress.py`** (new, ~15 lines) — pure function
  `summarize_progress(results: list[dict]) -> ProgressResponse`. No I/O, so it is
  trivially unit-testable. Kept out of `scoring.py` because it isn't scoring.
- **`app/main.py`** — thin `@app.get("/progress")` returning
  `summarize_progress(data.load_results())`.
- **`tests/test_progress.py`** (new) — unit tests for `summarize_progress`
  (empty, one record, several records, non-integer average) and one endpoint test
  using a temp results file.

Not touched: `scoring.py` (seeded bug/stubs stay, per CLAUDE.md guardrails),
`save_result()`, `/score`.

## 2. Order
1. `ProgressResponse` model.
2. `summarize_progress` + its unit tests → `pytest -q` green.
3. **Empty-results guard:** in `summarize_progress`, return
   `rounds_practised=0, average_total=None` *before* averaging when `results` is
   `[]`, so we never divide by zero. (Done — `app/progress.py`.)
4. `load_results()` in `data.py`.
5. `/progress` endpoint + endpoint test (temp file).
   - **Note — test to write:** one endpoint test where `results.json` exists but
     contains `[]` → expect `200 {"rounds_practised": 0, "average_total": null}`.
     (Covered so far: empty list at unit level, and a *missing* file at endpoint
     level — not yet an empty file at endpoint level.)
6. `pytest -q`, `ruff check .`, `mypy app`; hit `/progress` in `/docs`.

## 3. What could break / easy to get wrong
- **Empty file → division by zero.** Must return `0` / `null`, not crash.
- **Tests touching the real `data/results.json`.** `data.py` does
  `from .config import DATA_DIR`, so monkeypatching `app.config.DATA_DIR` does
  nothing — must patch **`app.data.DATA_DIR`** to a `tmp_path`.
- **Missing or malformed file** → unhandled exception → 500. Missing = treat as
  empty; malformed = let it fail loudly for now (don't silently report 0).
- **Averages look wrong today**: totals come from `compute_total()`, which has the
  seeded off-by-one bug. `/progress` faithfully reports bad data — not its bug to fix.
- **Integer division / rounding**: use true division and `round(x, 1)`.
- **Mixed `max` values**: averaging `total` assumes every record is out of the same
  max (20). Fine today; note it.
- It will always return `0` until `/score` actually calls `save_result()`.

## 4. Riskiest assumption
**That each record in `results.json` has a `round` and an integer `total` key.**
Nothing writes the file yet, so this is an unenforced contract between `/score`
(future writer) and `/progress` (reader). If Module 3 saves a different shape
(e.g. nests the scorecard, or names it `score`), `/progress` breaks with a
`KeyError`. De-risk: write the expected record shape down in the test fixtures now,
and have `/score` save exactly `{round, question_id, answer, total, max, ...}` when
it's wired up (later step, optionally via a Pydantic `ResultRecord`).

## Verification
- `pytest -q` — new tests pass, existing 3 still pass, real `results.json` unchanged.
- `ruff check .` and `mypy app` clean.
- `uvicorn app.main:app --reload` → `GET /progress` returns
  `{"rounds_practised": 0, "average_total": null}` on the empty file.
