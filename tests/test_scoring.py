"""Unit tests for app/scoring.py. Pure functions, no network, no disk."""
from __future__ import annotations

import pytest

from app.models import CategoryScore
from app.scoring import RUBRIC_CATEGORIES, compute_total, format_scorecard


def test_compute_total_sums_all_categories() -> None:
    categories = [
        CategoryScore(name=name, score=3, feedback="ok") for name in RUBRIC_CATEGORIES
    ]
    assert len(categories) == 4
    assert compute_total(categories) == 12


@pytest.mark.parametrize(
    ("total", "summary"),
    [
        (-1, "Needs significant work"),
        (0, "Needs significant work"),
        (4, "Needs significant work"),
        (5, "Needs work"),
        (9, "Needs work"),
        (10, "Solid, with gaps"),
        (15, "Solid, with gaps"),
        (16, "Strong answer"),
        (19, "Strong answer"),
        (20, "Strong answer - full marks"),
        (21, "Strong answer"),  # full marks is exactly 20, not "20 or more"
    ],
)
def test_format_scorecard_summary_bands(total: int, summary: str) -> None:
    categories = [CategoryScore(name="Only", score=total, feedback="ok")]
    assert format_scorecard(categories).summary == summary


def test_format_scorecard_max_and_total() -> None:
    categories = [
        CategoryScore(name=name, score=4, feedback="ok") for name in RUBRIC_CATEGORIES
    ]
    scorecard = format_scorecard(categories)
    assert scorecard.total == 16
    assert scorecard.max == 20
    assert scorecard.categories == categories


def test_format_scorecard_no_categories() -> None:
    scorecard = format_scorecard([])
    assert (scorecard.total, scorecard.max) == (0, 0)
    assert scorecard.summary == "Needs significant work"
