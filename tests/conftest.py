from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND = PROJECT_ROOT / "src" / "backend"
sys.path.insert(0, str(BACKEND))

RUNTIME = PROJECT_ROOT / ".test-runtime"
os.environ["STOREX_DATA_DIR"] = str(RUNTIME)
os.environ["STOREX_OUTPUT_DIR"] = str(RUNTIME / "output")
os.environ["STOREX_DB_PATH"] = str(RUNTIME / "test.db")

from main import app
from models import db_session


TABLES = (
    "personas", "materials_categories", "mix_templates", "batch_tasks",
    "publish_schedule", "publish_accounts", "settings", "licenses",
)


@pytest_asyncio.fixture
async def client():
    async with app.router.lifespan_context(app):
        async with db_session() as db:
            for table in TABLES:
                await db.execute(f"DELETE FROM {table}")
            await db.commit()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
            yield http
