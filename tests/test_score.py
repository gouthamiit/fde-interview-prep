"""Tests for POST /score. They never touch the real data/results.json."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import data
from app.main import app

client = TestClient(app)

BODY = {"round": "decomposition", "question_id": "dec-01", "answer": "Ask first.\nThen plan."}


@pytest.fixture
def results_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point app.data at a temp folder holding an empty results.json."""
    path = tmp_path / "results.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    return path


def test_score_returns_one_score_per_category(results_file: Path) -> None:
    resp = client.post("/score", json=BODY)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["categories"]) == 4
    assert body["max"] == 20


def test_score_saves_the_result(results_file: Path) -> None:
    resp = client.post("/score", json=BODY)
    saved = json.loads(results_file.read_text(encoding="utf-8"))
    assert len(saved) == 1
    assert saved[0]["question_id"] == "dec-01"
    assert saved[0]["total"] == resp.json()["total"]


def test_progress_counts_scored_answers(results_file: Path) -> None:
    client.post("/score", json=BODY)
    client.post("/score", json=BODY)
    assert client.get("/progress").json()["rounds_practised"] == 2


def test_score_missing_answer_is_422(results_file: Path) -> None:
    resp = client.post("/score", json={"round": "decomposition", "question_id": "dec-01"})
    assert resp.status_code == 422
