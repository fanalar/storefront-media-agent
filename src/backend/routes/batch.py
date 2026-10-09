"""Persistent batch-composition jobs."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from license_gate import require_active_license
from models import db_session, utc_now
from schemas import BatchInput
from video_service import VideoError, compose_video_async


router = APIRouter()
_running: set[asyncio.Task] = set()


async def _update(task_id: int, **values) -> None:
    if not values:
        return
    values["updated_at"] = utc_now()
    assignments = ",".join(f"{key}=?" for key in values)
    async with db_session() as db:
        await db.execute(
            f"UPDATE batch_tasks SET {assignments} WHERE id=?",
            (*values.values(), task_id),
        )
        await db.commit()


async def _run_batch(task_id: int, data: BatchInput) -> None:
    outputs: list[str] = []
    try:
        await _update(task_id, status="running")
        for index, template_id in enumerate(data.template_ids, start=1):
            async with db_session() as db:
                row = await (
                    await db.execute("SELECT * FROM mix_templates WHERE id=?", (template_id,))
                ).fetchone()
            if row is None:
                raise VideoError(f"模板 {template_id} 不存在")
            result = await compose_video_async(
                json.loads(row["clips_json"]),
                json.loads(row["options_json"]),
                f"{row['name']}_{task_id}_{index}.mp4",
                data.output_dir,
            )
            outputs.append(result["output_path"])
            await _update(
                task_id,
                completed=index,
                progress=round(index / len(data.template_ids) * 100, 2),
                request_json=json.dumps({**data.model_dump(), "outputs": outputs}, ensure_ascii=False),
            )
        await _update(task_id, status="done", progress=100)
    except Exception as exc:
        await _update(task_id, status="failed", error=str(exc)[:2000])


@router.get("/tasks")
async def get_tasks() -> list[dict]:
    async with db_session() as db:
        rows = await (await db.execute("SELECT * FROM batch_tasks ORDER BY id DESC")).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["request"] = json.loads(item.pop("request_json"))
        result.append(item)
    return result


@router.post("/start", status_code=202, dependencies=[Depends(require_active_license)])
async def start_task(data: BatchInput) -> dict:
    if data.output_dir and not Path(data.output_dir).expanduser().is_dir():
        raise HTTPException(400, "输出目录不存在")
    now = utc_now()
    async with db_session() as db:
        placeholders = ",".join("?" for _ in data.template_ids)
        count = (
            await (
                await db.execute(
                    f"SELECT COUNT(*) FROM mix_templates WHERE id IN ({placeholders})",
                    tuple(data.template_ids),
                )
            ).fetchone()
        )[0]
        if count != len(set(data.template_ids)):
            raise HTTPException(400, "批量任务包含不存在的模板")
        cursor = await db.execute(
            "INSERT INTO batch_tasks(status,total,completed,progress,output_dir,request_json,error,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
            ("pending", len(data.template_ids), 0, 0, data.output_dir, json.dumps(data.model_dump(), ensure_ascii=False), "", now, now),
        )
        await db.commit()
        task_id = cursor.lastrowid
    task = asyncio.create_task(_run_batch(task_id, data), name=f"batch-{task_id}")
    _running.add(task)
    task.add_done_callback(_running.discard)
    return {"success": True, "task_id": task_id}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int) -> dict:
    async with db_session() as db:
        row = await (await db.execute("SELECT status FROM batch_tasks WHERE id=?", (task_id,))).fetchone()
        if row is None:
            raise HTTPException(404, "任务不存在")
        if row["status"] == "running":
            raise HTTPException(409, "运行中的任务不能删除")
        await db.execute("DELETE FROM batch_tasks WHERE id=?", (task_id,))
        await db.commit()
    return {"success": True}


@router.delete("/completed")
async def clear_completed() -> dict:
    async with db_session() as db:
        cursor = await db.execute("DELETE FROM batch_tasks WHERE status IN ('done','failed')")
        await db.commit()
        return {"success": True, "deleted": cursor.rowcount}
