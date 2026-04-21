FROM python:3.12-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir fastapi 'uvicorn[standard]'

FROM python:3.12-slim

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV INDEX_PATH=/app/index.json

RUN useradd --create-home --uid 10001 appuser

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser app/main.py /app/main.py
COPY --chown=appuser:appuser out/index.json /app/index.json

USER appuser

EXPOSE 8092

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8092"]
