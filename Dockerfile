# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10

FROM node:20-bookworm-slim AS frontend
WORKDIR /frontend
COPY package.json package-lock.json ./
RUN npm ci

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

FROM python:${PYTHON_VERSION}-slim-bookworm

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=80

COPY --from=builder /app/.venv /app/.venv
COPY backend ./backend

COPY --from=frontend /frontend/node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/

COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

RUN useradd --create-home --uid 1000 app \
    && chown -R app:app /app \
    && chmod -R a+rX /app/public \
    && chmod +x /docker-entrypoint.sh \
    && rm -f /etc/nginx/sites-enabled/default

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
