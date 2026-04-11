.PHONY: dev migrate seed test test-backend test-frontend lint format typecheck build clean logs shell createsuperuser

# Development
dev:
	docker compose up --build

migrate:
	docker compose exec django python manage.py migrate

seed:
	docker compose exec django python manage.py seed_all

shell:
	docker compose exec django python manage.py shell_plus

createsuperuser:
	docker compose exec django python manage.py createsuperuser

# Testing
test: test-backend test-frontend

test-backend:
	docker compose exec django pytest --cov --cov-report=term-missing -v

test-frontend:
	docker compose exec react npx vitest run --coverage

# Code Quality
lint:
	docker compose exec django black --check .
	docker compose exec django isort --check-only .
	docker compose exec django flake8 .
	docker compose exec react npx eslint src/
	docker compose exec react npx prettier --check "src/**/*.{ts,tsx}"

format:
	docker compose exec django black .
	docker compose exec django isort .
	docker compose exec react npx prettier --write "src/**/*.{ts,tsx}"

typecheck:
	docker compose exec django mypy .
	docker compose exec react npx tsc --noEmit

# Build & Clean
build:
	docker compose build

clean:
	docker compose down -v --remove-orphans

logs:
	docker compose logs -f
