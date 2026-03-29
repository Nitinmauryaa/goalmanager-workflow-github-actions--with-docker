from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from backend.fastapi_app import main as fastapi_main
from backend.flask_app import app as flask_main


def test_fastapi_validate_payload_requires_title() -> None:
    with pytest.raises(HTTPException) as exc_info:
        fastapi_main.validate_payload({"description": "x"}, require_title=True)

    assert exc_info.value.status_code == 400


def test_fastapi_validate_payload_completed_type() -> None:
    with pytest.raises(HTTPException) as exc_info:
        fastapi_main.validate_payload({"title": "Read", "completed": "yes"}, require_title=True)

    assert exc_info.value.status_code == 400


def test_fastapi_create_goal_persists(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_file = data_dir / "goals.json"
    monkeypatch.setattr(fastapi_main, "DATA_DIR", data_dir)
    monkeypatch.setattr(fastapi_main, "DATA_FILE", data_file)

    created = fastapi_main.create_goal(
        {"title": "CI test", "description": "demo", "target_date": "2026-03-30"}
    )

    assert created["title"] == "CI test"
    goals = fastapi_main.load_goals()
    assert len(goals) == 1
    assert goals[0]["id"] == created["id"]


def test_flask_validate_payload_rules() -> None:
    is_valid, _ = flask_main.validate_payload({}, require_title=True)
    assert not is_valid

    is_valid, _ = flask_main.validate_payload(
        {"title": "Read", "completed": "yes"}, require_title=True
    )
    assert not is_valid


def test_flask_save_and_load_roundtrip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_file = data_dir / "goals.json"
    monkeypatch.setattr(flask_main, "DATA_DIR", data_dir)
    monkeypatch.setattr(flask_main, "DATA_FILE", data_file)

    expected = [
        {
            "id": "1",
            "title": "Write tests",
            "description": "backend checks",
            "target_date": "2026-03-30",
            "completed": False,
        }
    ]

    flask_main.save_goals(expected)
    loaded = flask_main.load_goals()
    assert loaded == expected
