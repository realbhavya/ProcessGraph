.PHONY: up down logs test lint build seed validate check-m1

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

test:
	python -m pytest -q backend

lint:
	cd backend && ruff check .

build:
	docker compose build

seed:
	./scripts/seed.sh

validate:
	python graph/validate.py

check-m1:
	./scripts/check_m1.sh
