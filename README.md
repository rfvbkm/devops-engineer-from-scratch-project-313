# devops-engineer-from-scratch-project-313

## Hexlet tests and linter status

[![Actions Status](https://github.com/rfvbkm/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/rfvbkm/devops-engineer-from-scratch-project-313/actions)

## CI (pytest, Ruff)

[![CI](https://github.com/rfvbkm/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/rfvbkm/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml)

## Деплой (Render)

Приложение: [https://devops-engineer-from-scratch-project-313-q6m6.onrender.com](https://devops-engineer-from-scratch-project-313-q6m6.onrender.com) — проверка: [GET /ping](https://devops-engineer-from-scratch-project-313-q6m6.onrender.com/ping).

## О проекте

Минимальное веб-приложение на **FastAPI**: точка входа — модуль `main.py` с объектом ASGI-приложения `app`, сервер **uvicorn**. Маршрут `GET /ping` отвечает телом `pong` (текст). Для ошибок валидации и неперехваченных исключений заданы обработчики с корректными HTTP-статусами (422 и 500). Линтер **Ruff** настраивается в `ruff.toml` (одинаково локально и в CI). Автоматические проверки — workflow **CI** (pytest и Ruff).

Мониторинг ошибок — **[Sentry](https://sentry.io/)**: при заданной переменной окружения **`SENTRY_DSN`** при старте вызывается `sentry_sdk.init` (интеграции Starlette и FastAPI). Собственный обработчик 500 отправляет исключение в Sentry через `capture_exception`.

**База и API сокращателя ссылок:** данные хранятся в **PostgreSQL**. При старте приложения вызывается `SQLModel.metadata.create_all` (создание таблиц при каждом запуске). REST API под префиксом **`/api/links`** (список, создание, чтение, обновление, удаление). Поле **`short_url`** собирается как `{SHORT_LINK_BASE}/{short_name}`.

Обязательные переменные окружения:

- **`DATABASE_URL`** — строка подключения к PostgreSQL (поддерживается префикс `postgres://`, он нормализуется в `postgresql://`), пример: `postgres://user:pass@host:5432/dbname?sslmode=disable`.
- **`SHORT_LINK_BASE`** — базовый URL без завершающего слэша, например `https://short.io/r` (итоговый `short_url`: `https://short.io/r/<short_name>`).

## Требования

- [Python](https://www.python.org/) 3.10+
- [uv](https://docs.astral.sh/uv/) для зависимостей и запуска
- [Node.js](https://nodejs.org/) 20+ для запуска фронтенда и `concurrently`
- [PostgreSQL](https://www.postgresql.org/) для работы приложения с данными (в тестах используется SQLite в памяти)

## Установка и запуск

Клонирование репозитория и установка зависимостей в виртуальное окружение (после смены ветки или удаления `.venv` выполните снова):

```bash
make install
# эквивалент: uv sync --all-groups
npm install
```

**Запуск только бэкенда** на порту **8080** (слушает на всех интерфейсах). Перед запуском задайте **`DATABASE_URL`** и **`SHORT_LINK_BASE`** (или пропишите их в `.env`):

```bash
export DATABASE_URL='postgres://postgres:password@localhost:5432/appdb?sslmode=disable'
export SHORT_LINK_BASE='https://example.com/r'
make run-backend
# эквивалент: uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

**Совместный запуск бэкенда (8080) и фронтенда (5173)** через `concurrently`:

```bash
make run FRAMEWORK=devops-deploy-crud
```

Фронтенд будет доступен на [http://localhost:5173/](http://localhost:5173/). Этот запуск нужен только для локальной проверки; в продакшене UI будет раздаваться веб-сервером. На бэкенде включен CORS для origin `http://localhost:5173`.

С Sentry (значение DSN возьмите из настроек проекта в Sentry, не коммитьте в git):

```bash
export SENTRY_DSN='https://<ключ>@<host>/<project_id>'
make run
```

В Docker: `docker run -e SENTRY_DSN -p 8080:8080 …`.

После старта проверка маршрута:

```bash
curl -s http://127.0.0.1:8080/ping
# ожидаемый вывод: pong
```

Линтер и тесты:

```bash
make lint
make test
```
