"""Publishing plans and account metadata.

Platform credentials are deliberately not stored in SQLite. Login and final
submission remain explicit user actions until an official platform adapter is
configured.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from license_gate import require_active_license
from models import db_session, utc_now
from schemas import PublishAccountInput, PublishScheduleInput


router = APIRouter()
PLATFORMS = [
    {"id": "douyin", "name": "抖音", "creator_url": "https://creator.douyin.com/", "mode": "manual_assist"},
    {"id": "wechat_channels", "name": "视频号", "creator_url": "https://channels.weixin.qq.com/", "mode": "manual_assist"},
    {"id": "kuaishou", "name": "快手", "creator_url": "https://cp.kuaishou.com/", "mode": "manual_assist"},
    {"id": "xiaohongshu", "name": "小红书", "creator_url": "https://creator.xiaohongshu.com/", "mode": "manual_assist"},
]


def _schedule(row) -> dict:
    item = dict(row)
    item["platforms"] = json.loads(item.pop("platforms_json"))
    item["topics"] = json.loads(item.pop("topics_json"))
    return item


@router.get("/platforms")
async def platforms() -> list[dict]:
    return PLATFORMS


@router.get("/schedule")
async def schedules() -> list[dict]:
    async with db_session() as db:
        rows = await (await db.execute("SELECT * FROM publish_schedule ORDER BY id DESC")).fetchall()
        return [_schedule(row) for row in rows]


@router.post("/schedule", status_code=201)
async def create_schedule(data: PublishScheduleInput) -> dict:
    path = Path(data.video_path).expanduser().resolve()
    if not path.is_file():
        raise HTTPException(400, "待发布视频不存在")
    supported = {item["id"] for item in PLATFORMS}
    if not set(data.platforms).issubset(supported):
        raise HTTPException(400, "包含不支持的发布平台")
    now = utc_now()
    async with db_session() as db:
        cursor = await db.execute(
            """INSERT INTO publish_schedule(video_path,title,platforms_json,topics_json,schedule_time,status,error,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                str(path),
                data.title,
                json.dumps(data.platforms, ensure_ascii=False),
                json.dumps(data.topics, ensure_ascii=False),
                data.schedule_time.isoformat() if data.schedule_time else "",
                "scheduled" if data.schedule_time else "draft",
                "",
                now,
                now,
            ),
        )
        await db.commit()
        return {"success": True, "id": cursor.lastrowid}


@router.delete("/schedule/{schedule_id}")
async def delete_schedule(schedule_id: int) -> dict:
    async with db_session() as db:
        cursor = await db.execute("DELETE FROM publish_schedule WHERE id=?", (schedule_id,))
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(404, "发布计划不存在")
    return {"success": True}


@router.get("/accounts")
async def accounts() -> list[dict]:
    async with db_session() as db:
        rows = await (await db.execute("SELECT * FROM publish_accounts ORDER BY id DESC")).fetchall()
        return [dict(row) for row in rows]


@router.post("/accounts", status_code=201)
async def save_account(data: PublishAccountInput) -> dict:
    now = utc_now()
    async with db_session() as db:
        try:
            cursor = await db.execute(
                """INSERT INTO publish_accounts(platform,account_name,account_id,status,created_at,updated_at)
                   VALUES(?,?,?,?,?,?)""",
                (data.platform, data.account_name, data.account_id, "not_connected", now, now),
            )
            await db.commit()
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise HTTPException(409, "该平台账号已经存在") from exc
            raise
        return {"success": True, "id": cursor.lastrowid}


@router.delete("/accounts/{account_id}")
async def delete_account(account_id: int) -> dict:
    async with db_session() as db:
        cursor = await db.execute("DELETE FROM publish_accounts WHERE id=?", (account_id,))
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(404, "账号不存在")
    return {"success": True}


@router.post("/schedule/{schedule_id}/prepare", dependencies=[Depends(require_active_license)])
async def prepare_publish(schedule_id: int) -> dict:
    async with db_session() as db:
        row = await (await db.execute("SELECT * FROM publish_schedule WHERE id=?", (schedule_id,))).fetchone()
    if row is None:
        raise HTTPException(404, "发布计划不存在")
    item = _schedule(row)
    return {
        "success": True,
        "mode": "manual_assist",
        "message": "已准备发布资料；平台登录和最终提交需要由用户确认",
        "schedule": item,
        "platforms": [platform for platform in PLATFORMS if platform["id"] in item["platforms"]],
    }
