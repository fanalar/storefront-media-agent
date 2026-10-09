"""SQLite schema and connection helpers."""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

import aiosqlite

from config import DB_PATH, ensure_runtime_dirs


SCHEMA = """
CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    name TEXT NOT NULL DEFAULT '',
    shop_name TEXT NOT NULL DEFAULT '',
    industry TEXT NOT NULL DEFAULT '',
    story TEXT NOT NULL DEFAULT '',
    speaking_style TEXT NOT NULL DEFAULT '',
    philosophy TEXT NOT NULL DEFAULT '',
    audience TEXT NOT NULL DEFAULT '',
    logo_path TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS materials_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    root_dir TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mix_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    clips_json TEXT NOT NULL DEFAULT '[]',
    options_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS batch_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL DEFAULT 'pending',
    total INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    progress REAL NOT NULL DEFAULT 0,
    output_dir TEXT NOT NULL DEFAULT '',
    request_json TEXT NOT NULL DEFAULT '{}',
    error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS publish_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_path TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    platforms_json TEXT NOT NULL DEFAULT '[]',
    topics_json TEXT NOT NULL DEFAULT '[]',
    schedule_time TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS publish_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_id TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'not_connected',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(platform, account_name)
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS licenses (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    token TEXT NOT NULL,
    license_id TEXT NOT NULL,
    plan TEXT NOT NULL,
    machine_hash TEXT NOT NULL,
    activated_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_verified_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_batch_status ON batch_tasks(status);
CREATE INDEX IF NOT EXISTS idx_publish_status_time ON publish_schedule(status, schedule_time);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def connect() -> aiosqlite.Connection:
    ensure_runtime_dirs()
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys=ON")
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA busy_timeout=5000")
    return db


@asynccontextmanager
async def db_session() -> AsyncIterator[aiosqlite.Connection]:
    db = await connect()
    try:
        yield db
    finally:
        await db.close()


async def init_db() -> None:
    async with db_session() as db:
        await db.executescript(SCHEMA)
        defaults: dict[str, Any] = {
            "auto_start": False,
            "minimize_to_tray": True,
            "publish_interval": 30,
            "theme": "dark",
            "language": "zh-CN",
            "ai_provider": "dashscope",
            "ai_model": "qwen-plus",
        }
        for key, value in defaults.items():
            await db.execute(
                "INSERT OR IGNORE INTO settings(key, value_json) VALUES(?, ?)",
                (key, json.dumps(value, ensure_ascii=False)),
            )
        await db.commit()


async def get_db() -> aiosqlite.Connection:
    """Compatibility helper for route modules and external integrations."""
    return await connect()

