# Tasks: GET /progress

Built from [`spec.md`](spec.md). Each task is one small change: make it, run
`pytest -q && ruff check . && mypy app`, then review it on its own. "AC n" means
acceptance criterion n in the spec.

Status as of 2026-11-08: T1–T5 are already in the codebase. T6 and T7 remain.

---

### T1 — `ProgressResponse` model ✅
- **Change:** `app/models.py`: add `ProgressResponse` with `rounds_practised: int` and
  `average_total: float | None`.
- **Test:** none of its own; T2 exercises it. `mypy app` passes.
- **Review:** the field names and types match the spec's table.

### T2 — `summarize_progress()` pure function ✅
- **Change:** a new file `app/progress.py` with
  `summarize_progress(results: list[dict]) -> ProgressResponse`. It does no I/O.
  An empty list returns `0` / `None` before any division.
- **Test:** `tests/test_progress.py` has unit tests for an empty list (AC 1),
  one record (AC 3), several records (AC 4) and rounding 10, 11, 11 → 10.7 (AC 5).
- **Review:** it uses true division and `round(x, 1)`, and reads only `record["total"]`.

### T3 — `data.load_results()` ✅
- **Change:** `app/data.py`: read `DATA_DIR / "results.json"` and return `[]` if the
  file is missing.
- **Test:** covered at endpoint level by the missing-file test in T4 (AC 2).
- **Review:** all file access stays in `data.py` (AC 7).

### T4 — Wire up `GET /progress` ✅
- **Change:** `app/main.py`: a one-line endpoint,
  `return summarize_progress(data.load_results())`, with return type `ProgressResponse`.
- **Test:** `tests/test_progress.py` has an endpoint test with a populated temp file
  (two results → `12.0`) and one with the file missing (AC 2). Both patch
  `app.data.DATA_DIR` (AC 8).
- **Review:** the endpoint contains no logic beyond the one line (AC 7).

### T5 — End-to-end with `/score` ✅
- **Change:** none. This task checks that `/score` saves records in the shape
  `/progress` reads.
- **Test:** `tests/test_score.py::test_progress_counts_scored_answers` posts two
  answers and expects `rounds_practised == 2`.
- **Review:** the test reads a temp file, not the real `results.json`.

### T6 — Endpoint test: file exists but contains `[]` ⬜
- **Change:** tests only. Add `test_progress_endpoint_empty_file_is_empty` to
  `tests/test_progress.py`: write `[]` to `tmp_path / "results.json"` and patch
  `app.data.DATA_DIR`.
- **Test:** `GET /progress` returns `200 {"rounds_practised": 0, "average_total": null}` (AC 1).
- **Review:** the test should pass without touching app code. If it fails, stop and
  treat the failure as a bug report.

### T7 — Endpoint test: `/progress` doesn't write the file ⬜
- **Change:** tests only. Add `test_progress_endpoint_is_read_only`: write a populated
  temp `results.json`, read its bytes, call `GET /progress`, then read the bytes again.
- **Test:** the bytes before and after are identical (AC 6).
- **Review:** the test makes no network calls and never touches the real data file.

---

**Out of scope here** (see the spec): zero-byte or malformed files, per-category
stats, filters, mixed `max` values. If any of these comes in, it starts its own
spec rather than becoming a task in this list.
