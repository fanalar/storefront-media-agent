"""Community edition metadata: no commercial activation or machine tracking."""
from __future__ import annotations

def community_status() -> dict:
    return {"activated": True, "valid": True, "success": True,
            "message": "MIT 社区版，无需激活", "plan": "MIT Community",
            "license_id": "community", "expires_at": None,
            "remaining_days": None, "community_edition": True}

async def license_status(db=None, machine_id=None) -> dict:
    return community_status()

async def local_license_status(db=None, machine_id=None) -> dict:
    return community_status()

async def activate_license(token=None, machine_id=None, db=None) -> dict:
    return community_status()
