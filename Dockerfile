# syntax=docker/dockerfile:1

FROM python:3.10-slim-bookworm AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY main.py config.py database.py models.py schemas.py ./
COPY routers ./routers

RUN uv sync --frozen --no-dev

FROM python:3.10-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY main.py config.py database.py models.py schemas.py ./
COPY routers ./routers

RUN useradd --create-home --uid 1000 app \
    && chown -R app:app /app

USER app

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
