"""Summarise practice history for GET /progress.

Pure functions only — no disk access — so the maths is easy to unit-test.
Each result record is expected to carry an integer `total` (see data.save_result).
"""
from __future__ import annotations

from .models import ProgressResponse


def summarize_progress(results: list[dict]) -> ProgressResponse:
    """Count the saved results and average their totals (None if there are none)."""
    if not results:
        return ProgressResponse(rounds_practised=0, average_total=None)
    totals = [record["total"] for record in results]
    average = round(sum(totals) / len(totals), 1)
    return ProgressResponse(rounds_practised=len(results), average_total=average)
