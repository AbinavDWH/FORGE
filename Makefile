.PHONY: install run test seed lint dev frontend

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --port 8000

test:
	python -m pytest tests/ -v

seed:
	python scripts/seed_demo_data.py

lint:
	ruff check app/

dev:
	uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev

frontend:
	cd frontend && npm install && npm run dev