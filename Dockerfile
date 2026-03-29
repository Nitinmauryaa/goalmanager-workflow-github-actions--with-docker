FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/tmp \
    PORT=8000 \
    WORKERS=2 \
    BACKEND=fastapi

WORKDIR /app

# Create non-root user
RUN addgroup --system app && adduser --system --ingroup app app

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn uvicorn

# Copy project files
COPY --chown=app:app backend ./backend
COPY --chown=app:app frontend ./frontend
COPY --chown=app:app data ./data

USER app

EXPOSE 8000

CMD ["sh", "-c", "if [ \"$BACKEND\" = \"flask\" ]; then gunicorn --bind 0.0.0.0:${PORT} --workers ${WORKERS} backend.flask_app.app:app; else gunicorn --bind 0.0.0.0:${PORT} --workers ${WORKERS} --worker-class uvicorn.workers.UvicornWorker backend.fastapi_app.main:app; fi"]