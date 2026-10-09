"""Compatibility endpoints for the MIT community edition."""
from fastapi import APIRouter
from activation import community_status
from schemas import LicenseActivateInput

router = APIRouter()

@router.get("/machine")
async def get_machine() -> dict:
    return {"machine_id": "", "machine_code": "MIT-COMMUNITY"}

@router.post("/activate")
async def activate(data: LicenseActivateInput) -> dict:
    return community_status()

@router.get("/status")
@router.get("/info")
async def status() -> dict:
    return community_status()
