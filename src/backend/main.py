"""FastAPI entry point for the local desktop service."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import API_TOKEN, APP_NAME, APP_VERSION, HOST, OUTPUT_DIR, PORT, ensure_runtime_dirs
from models import db_session, init_db, utc_now
from routes.ai import router as ai_router
from routes.batch import router as batch_router
from routes.license import router as license_router
from routes.materials import router as materials_router
from routes.mix import router as mix_router
from routes.persona import router as persona_router
from routes.publish import router as publish_router
from routes.settings import router as settings_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_runtime_dirs()
    await init_db()
    async with db_session() as db:
        await db.execute(
            "UPDATE batch_tasks SET status='interrupted',error='应用在任务完成前退出',updated_at=? WHERE status='running'",
            (utc_now(),),
        )
        await db.commit()
    yield


ensure_runtime_dirs()
app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    # Vite uses an HTTP origin in development; the packaged Electron renderer
    # loads from file:// and therefore sends the literal `null` origin.
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "null"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def local_token_guard(request: Request, call_next):
    # A CORS preflight carries the requested header name, not its secret value.
    # Let CORSMiddleware answer it; the following real request is still guarded.
    if request.method != "OPTIONS" and API_TOKEN and request.url.path not in {"/health", "/api/health"}:
        if request.headers.get("X-StoreX-Token") != API_TOKEN:
            return JSONResponse({"detail": "本地服务令牌无效"}, status_code=401)
    return await call_next(request)


app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
app.include_router(license_router, prefix="/api/license", tags=["授权"])
app.include_router(persona_router, prefix="/api/persona", tags=["人设"])
app.include_router(materials_router, prefix="/api/materials", tags=["素材"])
app.include_router(mix_router, prefix="/api/mix", tags=["混剪"])
app.include_router(batch_router, prefix="/api/batch", tags=["批量"])
app.include_router(publish_router, prefix="/api/publish", tags=["发布"])
app.include_router(settings_router, prefix="/api/settings", tags=["设置"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])


@app.get("/health")
@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "name": APP_NAME, "version": APP_VERSION, "port": PORT}


@app.get("/api/capabilities")
async def capabilities() -> dict:
    return {
        "video_compose": True,
        "batch_compose": True,
        "ai_script": True,
        "commercial_features_require_license": False,
        "community_edition": True,
        "publish_mode": "manual_assist",
        "publish_note": "平台登录和最终提交必须由用户确认",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
