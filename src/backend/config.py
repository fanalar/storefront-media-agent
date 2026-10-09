"""Application paths and runtime configuration.

Customer data is stored outside the installation directory when Electron sets
``STOREX_DATA_DIR``. Development defaults stay inside ``src/backend/data``.
"""
from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "实体店新媒体AI智能体"
APP_VERSION = "0.2.0-community.1"
BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("STOREX_DATA_DIR", BACKEND_DIR / "data")).resolve()
OUTPUT_DIR = Path(os.environ.get("STOREX_OUTPUT_DIR", DATA_DIR / "output")).resolve()
DB_PATH = Path(os.environ.get("STOREX_DB_PATH", DATA_DIR / "storex.db")).resolve()
HOST = os.environ.get("STOREX_BACKEND_HOST", "127.0.0.1")
PORT = int(os.environ.get("STOREX_BACKEND_PORT", "35107"))
API_TOKEN = os.environ.get("STOREX_API_TOKEN", "")


def ensure_runtime_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

