.PHONY: up dev-api dev-worker lint typecheck test

up:
	docker compose -f deploy/docker/compose.dev.yml up -d

dev-api:
	poetry -C apps/api run uvicorn nimbus.main:app --reload --host 0.0.0.0 --port 8000

dev-worker:
	poetry -C apps/worker run python -m nimbus_worker.worker

lint:
	poetry -C apps/api run ruff check .
	poetry -C apps/worker run ruff check .

typecheck:
	poetry -C apps/api run mypy --config-file mypy.ini .
	poetry -C apps/worker run mypy --config-file mypy.ini .

test:
	poetry -C apps/api run pytest -q --maxfail=1 --disable-warnings
	poetry -C apps/worker run pytest -q --maxfail=1 --disable-warnings
