from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "goals.json"

app = FastAPI(title="Goal Manager API")


def load_goals() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_goals(goals: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(goals, file, indent=2)


def validate_payload(payload: dict[str, Any], require_title: bool) -> None:
    title = payload.get("title")
    if require_title and (not isinstance(title, str) or not title.strip()):
        raise HTTPException(status_code=400, detail="title is required")

    if "completed" in payload and not isinstance(payload["completed"], bool):
        raise HTTPException(status_code=400, detail="completed must be true or false")


@app.get("/api/goals")
def list_goals() -> list[dict[str, Any]]:
    return load_goals()


@app.post("/api/goals", status_code=201)
def create_goal(payload: dict[str, Any]) -> dict[str, Any]:
    validate_payload(payload, require_title=True)

    goal = {
        "id": str(uuid4()),
        "title": payload["title"].strip(),
        "description": str(payload.get("description", "")).strip(),
        "target_date": str(payload.get("target_date", "")).strip(),
        "completed": bool(payload.get("completed", False)),
    }

    goals = load_goals()
    goals.append(goal)
    save_goals(goals)
    return goal


@app.put("/api/goals/{goal_id}")
def update_goal(goal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    validate_payload(payload, require_title=False)

    goals = load_goals()
    for goal in goals:
        if goal["id"] == goal_id:
            if "title" in payload:
                if not isinstance(payload["title"], str) or not payload["title"].strip():
                    raise HTTPException(status_code=400, detail="title cannot be empty")
                goal["title"] = payload["title"].strip()
            if "description" in payload:
                goal["description"] = str(payload["description"]).strip()
            if "target_date" in payload:
                goal["target_date"] = str(payload["target_date"]).strip()
            if "completed" in payload:
                goal["completed"] = payload["completed"]

            save_goals(goals)
            return goal

    raise HTTPException(status_code=404, detail="goal not found")


@app.delete("/api/goals/{goal_id}")
def delete_goal(goal_id: str) -> dict[str, str]:
    goals = load_goals()
    filtered_goals = [goal for goal in goals if goal["id"] != goal_id]

    if len(filtered_goals) == len(goals):
        raise HTTPException(status_code=404, detail="goal not found")

    save_goals(filtered_goals)
    return {"message": "goal deleted"}


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
