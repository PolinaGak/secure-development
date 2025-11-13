import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_jwt_from_env():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Регистрация
        resp = await client.post(
            "/auth/register",
            json={
                "username": "secretuser",
                "email": "secret@example.com",
                "password": "secret123",
            },
        )
        assert resp.status_code == 200

        # Логин
        resp = await client.post(
            "/auth/login", data={"username": "secretuser", "password": "secret123"}
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        assert len(token) > 50  # JWT
