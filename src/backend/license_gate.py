"""Community edition has no commercial feature gate.

The independent local API token middleware remains enabled in Electron.
"""
async def require_active_license() -> None:
    return None
