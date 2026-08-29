# FORGE

Field Operations Reconciliation & Gantt Engine.

FORGE converts informal field updates into trusted schedule progress while preserving CPM logic and producing auditable proof.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

API docs:
http://127.0.0.1:8000/docs


---

# 3. Backend core files

## `app/config.py`

```python
from app.core.settings import settings

__all__ = ["settings"]