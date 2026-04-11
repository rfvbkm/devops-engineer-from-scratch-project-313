install:
	uv sync --all-groups

run:
	uv run uvicorn main:app --host 0.0.0.0 --port 8080

lint:
	uv run ruff check .

test:
	uv run pytest
