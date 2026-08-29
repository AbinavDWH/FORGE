.PHONY: install run

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --port 8000