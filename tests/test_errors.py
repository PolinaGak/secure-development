# tests/test_errors.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Not Found"  # ← стандартный FastAPI
