from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "goals.json"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


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


def validate_payload(payload: dict[str, Any], require_title: bool) -> tuple[bool, str]:
    title = payload.get("title")
    if require_title and (not isinstance(title, str) or not title.strip()):
        return False, "title is required"

    if "completed" in payload and not isinstance(payload["completed"], bool):
        return False, "completed must be true or false"

    return True, ""


@app.get("/api/goals")
def list_goals() -> tuple[Any, int]:
    goals = load_goals()
    return jsonify(goals), 200


@app.post("/api/goals")
def create_goal() -> tuple[Any, int]:
    payload = request.get_json(silent=True) or {}
    is_valid, error = validate_payload(payload, require_title=True)
    if not is_valid:
        return jsonify({"error": error}), 400

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
    return jsonify(goal), 201


@app.put("/api/goals/<goal_id>")
def update_goal(goal_id: str) -> tuple[Any, int]:
    payload = request.get_json(silent=True) or {}
    is_valid, error = validate_payload(payload, require_title=False)
    if not is_valid:
        return jsonify({"error": error}), 400

    goals = load_goals()
    for goal in goals:
        if goal["id"] == goal_id:
            if "title" in payload:
                if not isinstance(payload["title"], str) or not payload["title"].strip():
                    return jsonify({"error": "title cannot be empty"}), 400
                goal["title"] = payload["title"].strip()
            if "description" in payload:
                goal["description"] = str(payload["description"]).strip()
            if "target_date" in payload:
                goal["target_date"] = str(payload["target_date"]).strip()
            if "completed" in payload:
                goal["completed"] = payload["completed"]

            save_goals(goals)
            return jsonify(goal), 200

    return jsonify({"error": "goal not found"}), 404


@app.delete("/api/goals/<goal_id>")
def delete_goal(goal_id: str) -> tuple[Any, int]:
    goals = load_goals()
    filtered_goals = [goal for goal in goals if goal["id"] != goal_id]

    if len(filtered_goals) == len(goals):
        return jsonify({"error": "goal not found"}), 404

    save_goals(filtered_goals)
    return jsonify({"message": "goal deleted"}), 200


@app.get("/")
def index() -> Any:
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
