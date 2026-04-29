FRAMEWORK ?= devops-deploy-crud

install:
	uv sync --all-groups
	npm install

run-backend:
	uv run uvicorn backend.main:app --host 0.0.0.0 --port 8080

run-frontend:
	npx start-hexlet-$(FRAMEWORK)-frontend

run:
	npx concurrently \
		--names backend,frontend \
		--prefix-colors blue,green \
		"make run-backend" \
		"make run-frontend FRAMEWORK=$(FRAMEWORK)"

lint:
	uv run ruff check .

test:
	uv run pytest
