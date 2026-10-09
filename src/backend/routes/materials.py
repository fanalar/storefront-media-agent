from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from models import db_session, utc_now
from schemas import CategoryInput
from video_service import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, VideoError, probe_media


router = APIRouter()
SUPPORTED = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS


@router.get("/scan")
async def scan(root_dir: str, recursive: bool = False, limit: int = Query(1000, ge=1, le=5000)) -> dict:
    root = Path(root_dir).expanduser().resolve()
    if not root.is_dir():
        raise HTTPException(400, "素材目录不存在")
    iterator = root.rglob("*") if recursive else root.iterdir()
    files = []
    for path in iterator:
        if path.is_file() and path.suffix.lower() in SUPPORTED:
            stat = path.stat()
            files.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "size": stat.st_size,
                    "type": "video" if path.suffix.lower() in VIDEO_EXTENSIONS else "image",
                    "modified_at": stat.st_mtime,
                }
            )
            if len(files) >= limit:
                break
    files.sort(key=lambda item: item["name"].casefold())
    return {"root_dir": str(root), "files": files, "truncated": len(files) >= limit}


@router.get("/preview")
async def preview(path: str):
    media = Path(path).expanduser().resolve()
    if not media.is_file() or media.suffix.lower() not in SUPPORTED:
        raise HTTPException(404, "素材不存在或格式不受支持")
    return FileResponse(media)


@router.get("/probe")
async def probe(path: str) -> dict:
    try:
        return probe_media(path)
    except VideoError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/categories")
async def categories() -> list[dict]:
    async with db_session() as db:
        rows = await (await db.execute("SELECT * FROM materials_categories ORDER BY id DESC")).fetchall()
        return [dict(row) for row in rows]


@router.post("/category", status_code=201)
async def create_category(data: CategoryInput) -> dict:
    root = Path(data.root_dir).expanduser().resolve()
    if not root.is_dir():
        raise HTTPException(400, "素材目录不存在")
    async with db_session() as db:
        try:
            cursor = await db.execute(
                "INSERT INTO materials_categories(name,root_dir,created_at) VALUES(?,?,?)",
                (data.name, str(root), utc_now()),
            )
            await db.commit()
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise HTTPException(409, "该目录已经创建过分类") from exc
            raise
        return {"success": True, "id": cursor.lastrowid}


@router.delete("/category/{category_id}")
async def delete_category(category_id: int) -> dict:
    async with db_session() as db:
        cursor = await db.execute("DELETE FROM materials_categories WHERE id=?", (category_id,))
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(404, "分类不存在")
    return {"success": True}

