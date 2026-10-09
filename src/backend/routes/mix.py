import json

from fastapi import APIRouter, Depends, HTTPException

from license_gate import require_active_license
from models import db_session, utc_now
from schemas import ComposeInput, TemplateInput
from video_service import VideoError, compose_video_async


router = APIRouter()


def _template(row) -> dict:
    item = dict(row)
    item["clips"] = json.loads(item.pop("clips_json"))
    item["options"] = json.loads(item.pop("options_json"))
    return item


@router.get("/templates")
async def list_templates() -> list[dict]:
    async with db_session() as db:
        rows = await (await db.execute("SELECT * FROM mix_templates ORDER BY updated_at DESC")).fetchall()
        return [_template(row) for row in rows]


@router.post("/templates", status_code=201)
async def save_template(data: TemplateInput) -> dict:
    now = utc_now()
    async with db_session() as db:
        cursor = await db.execute(
            "INSERT INTO mix_templates(name,clips_json,options_json,created_at,updated_at) VALUES(?,?,?,?,?)",
            (
                data.name,
                json.dumps([shot.model_dump() for shot in data.clips], ensure_ascii=False),
                json.dumps(data.options.model_dump(), ensure_ascii=False),
                now,
                now,
            ),
        )
        await db.commit()
        return {"success": True, "id": cursor.lastrowid}


@router.put("/templates/{template_id}")
async def update_template(template_id: int, data: TemplateInput) -> dict:
    async with db_session() as db:
        cursor = await db.execute(
            "UPDATE mix_templates SET name=?,clips_json=?,options_json=?,updated_at=? WHERE id=?",
            (
                data.name,
                json.dumps([shot.model_dump() for shot in data.clips], ensure_ascii=False),
                json.dumps(data.options.model_dump(), ensure_ascii=False),
                utc_now(),
                template_id,
            ),
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(404, "模板不存在")
    return {"success": True}


@router.delete("/templates/{template_id}")
async def delete_template(template_id: int) -> dict:
    async with db_session() as db:
        cursor = await db.execute("DELETE FROM mix_templates WHERE id=?", (template_id,))
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(404, "模板不存在")
    return {"success": True}


@router.post("/compose", dependencies=[Depends(require_active_license)])
async def compose(data: ComposeInput) -> dict:
    shots = [shot.model_dump() for shot in data.shots]
    options = data.options.model_dump()
    if data.template_id:
        async with db_session() as db:
            row = await (await db.execute("SELECT * FROM mix_templates WHERE id=?", (data.template_id,))).fetchone()
        if row is None:
            raise HTTPException(404, "模板不存在")
        if not shots:
            shots = json.loads(row["clips_json"])
        if data.options == data.options.__class__():
            options = json.loads(row["options_json"])
    try:
        return await compose_video_async(shots, options, data.output_name)
    except VideoError as exc:
        raise HTTPException(400, str(exc)) from exc
