# devops-engineer-from-scratch-project-313

### Hexlet tests and linter status

[![Actions Status](https://github.com/rfvbkm/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/rfvbkm/devops-engineer-from-scratch-project-313/actions)

### CI (pytest, Ruff)

[![CI](https://github.com/rfvbkm/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/rfvbkm/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml)

## О проекте

Минимальное веб-приложение на **FastAPI**: точка входа — модуль `main.py` с объектом ASGI-приложения `app`, сервер **uvicorn**. Маршрут `GET /ping` отвечает телом `pong` (текст). Для ошибок валидации и неперехваченных исключений заданы обработчики с корректными HTTP-статусами (422 и 500). Линтер **Ruff** настраивается в `ruff.toml` (одинаково локально и в CI). Автоматические проверки — workflow **CI** (pytest и Ruff).

Мониторинг ошибок — **[Sentry](https://sentry.io/)**: при заданной переменной окружения **`SENTRY_DSN`** при старте вызывается `sentry_sdk.init` (интеграции Starlette и FastAPI). Собственный обработчик 500 отправляет исключение в Sentry через `capture_exception`.

## Требования

- [Python](https://www.python.org/) 3.10+
- [uv](https://docs.astral.sh/uv/) для зависимостей и запуска

## Установка и запуск

Клонирование репозитория и установка зависимостей в виртуальное окружение (после смены ветки или удаления `.venv` выполните снова):

```bash
make install
# эквивалент: uv sync --all-groups
```

**Запуск HTTP-сервера** на порту **8080** (слушает на всех интерфейсах):

```bash
make run
# эквивалент: uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

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
