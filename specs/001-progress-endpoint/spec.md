# Spec: GET /progress

Status: implemented. See `plans/001-progress-endpoint-plan.md` for the build plan.

## Why
Candidates practise over many mock rounds and need a quick answer to "am I
practising enough, and am I improving?" without reading `data/results.json`
by hand. `/progress` gives them a one-call summary of their practice history.

## What it returns
`200 OK` with a `ProgressResponse` (`app/models.py`):

```json
{"rounds_practised": 3, "average_total": 14.0}
```

| Field              | Type            | Meaning                                                  |
|--------------------|-----------------|----------------------------------------------------------|
| `rounds_practised` | `int`           | Number of saved results (attempts, not distinct rounds). |
| `average_total`    | `float \| null` | Mean of each result's `total`, rounded to 1 dp; `null` when there are none. |

## What it reads
- `data/results.json` only, via `data.load_results()` (a JSON list of result records).
- From each record it uses only `total` (an `int`, out of 20). Records are written by
  `POST /score` through `data.save_result()`.
- It never writes and never calls OpenAI.

## Acceptance criteria
1. **Empty list:** if `results.json` contains `[]`, the response is
   `200 {"rounds_practised": 0, "average_total": null}` (no division by zero).
2. **Missing file:** if `results.json` doesn't exist, the response is the same as
   for an empty list.
3. **One result** with `total` 12 → `{"rounds_practised": 1, "average_total": 12.0}`.
4. **Several results** with totals 10, 14, 18 → `{"rounds_practised": 3, "average_total": 14.0}`.
5. **Rounding:** totals 10, 11, 11 → `average_total` 10.7 (true division, then `round(x, 1)`).
6. **Read-only:** calling `/progress` leaves `results.json` byte-for-byte unchanged.
7. **Layering:** the endpoint in `main.py` is one line; the maths lives in the pure
   function `progress.summarize_progress()`; file access happens only in `data.py`.
8. **Tests run offline** against a temporary results file (patch `app.data.DATA_DIR`);
   they never touch the real `data/results.json`.

## Out of scope
- Per-category averages, the weakest category, and trends over time (the `/report`
  skill covers these for now).
- Filtering by round, question or date range.
- Handling a malformed file. Invalid JSON, including a zero-byte file, currently
  fails loudly with a 500 rather than reporting 0.
- Records with different `max` values. The average assumes every total is out of 20.
- Fixing totals that are wrong at the source: `/progress` reports what `/score` saved.
- Auth, multiple users, pagination.
