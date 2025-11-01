import pytest
from httpx import AsyncClient, ASGITransport
from nimbus.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = "testuser@example.com"
        password = "Testpass123"
        # Register
        resp = await ac.post("/v1/auth/register", json={"email": email, "password": password})
        assert resp.status_code in (200, 409)  # 409 if already exists
        # Login
        resp = await ac.post("/v1/auth/login", json={"email": email, "password": password})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

@pytest.mark.asyncio
async def test_project_create():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register/login
        email = "projuser@example.com"
        password = "Projpass123"
        await ac.post("/v1/auth/register", json={"email": email, "password": password})
        login = await ac.post("/v1/auth/login", json={"email": email, "password": password})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Create project
        resp = await ac.post("/v1/projects", json={"name": "Test Project"}, headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert "project" in data
        assert "api_key_id" in data
        assert "api_key_secret" in data
