"""Tests for GET /progress and the summarize_progress() helper.

These tests never touch the real data/results.json: the endpoint test points
app.data.DATA_DIR at a temporary folder.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import data
from app.main import app
from app.progress import summarize_progress

client = TestClient(app)


def make_record(total: int, round: str = "decomposition") -> dict:
    """One results.json record, in the shape /score is expected to save."""
    return {"round": round, "question_id": "dec-01", "answer": "...", "total": total, "max": 20}


def test_summarize_empty_has_no_average() -> None:
    progress = summarize_progress([])
    assert progress.rounds_practised == 0
    assert progress.average_total is None


def test_summarize_single_record() -> None:
    progress = summarize_progress([make_record(12)])
    assert progress.rounds_practised == 1
    assert progress.average_total == 12.0


def test_summarize_several_records() -> None:
    progress = summarize_progress([make_record(10), make_record(14), make_record(18)])
    assert progress.rounds_practised == 3
    assert progress.average_total == 14.0


def test_summarize_rounds_non_integer_average() -> None:
    progress = summarize_progress([make_record(10), make_record(11), make_record(11)])
    assert progress.average_total == 10.7  # 32 / 3 = 10.666...


def test_progress_endpoint_reads_results_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results = [make_record(8), make_record(16, round="behavioral")]
    (tmp_path / "results.json").write_text(json.dumps(results), encoding="utf-8")
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)

    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {"rounds_practised": 2, "average_total": 12.0}


def test_progress_endpoint_missing_file_is_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)  # no results.json in here

    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {"rounds_practised": 0, "average_total": None}


def test_progress_endpoint_empty_file_is_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "results.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)

    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {"rounds_practised": 0, "average_total": None}
