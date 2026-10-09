import json

from fastapi import APIRouter

from models import db_session
from schemas import SettingsInput


router = APIRouter()


@router.get("")
async def get_settings() -> dict:
    async with db_session() as db:
        rows = await (await db.execute("SELECT key,value_json FROM settings")).fetchall()
    result = {}
    for row in rows:
        try:
            result[row["key"]] = json.loads(row["value_json"])
        except json.JSONDecodeError:
            result[row["key"]] = row["value_json"]
    return result


@router.put("")
@router.post("")
async def save_settings(data: SettingsInput) -> dict:
    values = data.model_dump(exclude_none=True)
    async with db_session() as db:
        for key, value in values.items():
            await db.execute(
                "INSERT INTO settings(key,value_json) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json",
                (key, json.dumps(value, ensure_ascii=False)),
            )
        await db.commit()
    return {"success": True, "saved": sorted(values)}

