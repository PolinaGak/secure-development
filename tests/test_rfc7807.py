import uuid

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_rfc7807_format_and_correlation_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/wishlists/999/items")

        assert response.status_code == 404
        data = response.json()

        # RFC 7807
        assert data["type"] == "https://api.wishlist.com/errors/wishlist-not-found"
        assert data["title"] == "Wishlist Not Found"
        assert data["status"] == 404
        assert data["detail"] == "Вишлист не найден"
        assert "instance" in data
        assert "correlation_id" in data

        # Заголовок
        assert response.headers["X-Correlation-ID"] == data["correlation_id"]

        # UUID валидный
        uuid.UUID(data["correlation_id"])
