from fastapi import APIRouter

from models import db_session, utc_now
from schemas import PersonaInput


router = APIRouter()


@router.get("")
async def get_persona() -> dict:
    async with db_session() as db:
        row = await (await db.execute("SELECT * FROM personas WHERE id=1")).fetchone()
        return dict(row) if row else {}


@router.put("")
@router.post("")
async def save_persona(data: PersonaInput) -> dict:
    now = utc_now()
    values = data.model_dump()
    async with db_session() as db:
        await db.execute(
            """INSERT INTO personas(id,name,shop_name,industry,story,speaking_style,philosophy,audience,logo_path,created_at,updated_at)
               VALUES(1,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 name=excluded.name,shop_name=excluded.shop_name,industry=excluded.industry,
                 story=excluded.story,speaking_style=excluded.speaking_style,
                 philosophy=excluded.philosophy,audience=excluded.audience,
                 logo_path=excluded.logo_path,updated_at=excluded.updated_at""",
            (*values.values(), now, now),
        )
        await db.commit()
    return {"success": True, "persona": {"id": 1, **values, "updated_at": now}}

