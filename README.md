# Goal Manager (Flask + FastAPI)

Goal Manager is a web app where you can create, track, complete, and delete goals.

The project includes:
- Frontend: HTML, CSS, JavaScript
- Backend option 1: Flask
- Backend option 2: FastAPI
- Local persistence: data/goals.json
- Tests: pytest
- Containerization: Docker
- CI/CD: GitHub Actions (test, smoke checks, Docker build, Docker publish)

Both Flask and FastAPI serve the same frontend and expose the same REST API.

## Features

- Add a goal
- View all goals
- Mark goal done or open
- Delete goal

## Project Structure

- backend/flask_app/app.py
- backend/fastapi_app/main.py
- frontend/index.html
- frontend/app.js
- data/goals.json
- tests/test_goal_manager.py
- .github/workflows/ci.yml

## Setup

1. Create and activate virtual environment.
2. Install dependencies.

```bash
python3 -m pip install -r requirements.txt
```

## Run Locally

### Run with Flask

```bash
python3 backend/flask_app/app.py
```

Open: http://127.0.0.1:5000

### Run with FastAPI

```bash
uvicorn backend.fastapi_app.main:app --reload --port 8000
```

Open: http://127.0.0.1:8000

## Test Locally

Use the project virtual environment interpreter for reliable test runs:

```bash
python3 -m pip install pytest
python3 -m pytest -q
```

## Docker

### Build image

```bash
docker build -t goal-manager .
```

### Run container (FastAPI mode by default)

```bash
docker run --rm -p 8000:8000 goal-manager
```

### Run container with Flask mode

```bash
docker run --rm -p 8000:8000 -e BACKEND=flask goal-manager
```

### Optional: persist data to host

```bash
docker run --rm -p 8000:8000 -v "$(pwd)/data:/app/data" goal-manager
```

## API Endpoints

- GET /api/goals
- POST /api/goals
- PUT /api/goals/{goal_id}
- DELETE /api/goals/{goal_id}

Example POST body:

```json
{
  "title": "Read 20 pages",
  "description": "Start with chapter 3",
  "target_date": "2026-03-30"
}
```

## GitHub Actions CI/CD

Workflow file: .github/workflows/ci.yml

On push and pull request, the workflow runs:
- Lint/syntax checks
- Pytest
- Flask API smoke test
- FastAPI API smoke test
- Docker build smoke test

On push and workflow_dispatch, after checks pass, workflow can publish Docker image to Docker Hub.

Required repository secrets for publish:
- DOCKERHUB_USERNAME
- DOCKERHUB_TOKEN
# goalmanager-workflow-github-actions--with-docker
