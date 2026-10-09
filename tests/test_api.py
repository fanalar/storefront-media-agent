from __future__ import annotations

import sys
from pathlib import Path

import pytest




@pytest.mark.asyncio
async def test_health_and_capabilities(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    capabilities = (await client.get("/api/capabilities")).json()
    assert capabilities["video_compose"] is True
    assert capabilities["publish_mode"] == "manual_assist"


@pytest.mark.asyncio
async def test_desktop_cors_preflight_is_not_blocked(client):
    response = await client.options(
        "/api/persona",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "x-storex-token,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


@pytest.mark.asyncio
async def test_persona_round_trip(client):
    payload = {
        "name": "张老板",
        "shop_name": "老张面馆",
        "industry": "餐饮",
        "story": "十年只做好一碗面",
        "speaking_style": "真诚直接",
        "philosophy": "当天食材当天用",
        "audience": "附近上班族",
        "logo_path": "",
    }
    saved = await client.put("/api/persona", json=payload)
    assert saved.status_code == 200
    loaded = await client.get("/api/persona")
    assert loaded.json()["shop_name"] == payload["shop_name"]


@pytest.mark.asyncio
async def test_material_category_scan_and_delete(client, tmp_path):
    (tmp_path / "门店.jpg").write_bytes(b"not-a-real-image")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    created = await client.post(
        "/api/materials/category", json={"name": "门店展示", "root_dir": str(tmp_path)}
    )
    assert created.status_code == 201
    category_id = created.json()["id"]
    scanned = await client.get("/api/materials/scan", params={"root_dir": str(tmp_path)})
    assert [item["name"] for item in scanned.json()["files"]] == ["门店.jpg"]
    deleted = await client.delete(f"/api/materials/category/{category_id}")
    assert deleted.status_code == 200


@pytest.mark.asyncio
async def test_template_crud(client):
    template = {
        "name": "餐饮口播",
        "clips": [{"path": "C:/placeholder.mp4", "duration": 3, "script": "欢迎光临", "role": "老板"}],
        "options": {"resolution": "720p", "subtitle_enabled": True},
    }
    created = await client.post("/api/mix/templates", json=template)
    assert created.status_code == 201
    template_id = created.json()["id"]
    items = (await client.get("/api/mix/templates")).json()
    assert any(item["id"] == template_id and item["clips"][0]["script"] == "欢迎光临" for item in items)
    assert (await client.delete(f"/api/mix/templates/{template_id}")).status_code == 200


@pytest.mark.asyncio
async def test_community_compose_is_not_commercially_gated(client):
    status = (await client.get("/api/license/status")).json()
    assert status["valid"] and status["community_edition"]
    response = await client.post("/api/mix/compose", json={"shots": [], "options": {}})
    assert response.status_code == 400
    assert (await client.get("/api/license/machine")).json()["machine_id"] == ""

@pytest.mark.asyncio
async def test_local_api_token_still_protects_actions(client, monkeypatch):
    import main
    monkeypatch.setattr(main, "API_TOKEN", "local-test")
    assert (await client.get("/api/persona")).status_code == 401
    assert (await client.get("/api/persona", headers={"X-StoreX-Token":"local-test"})).status_code == 200
