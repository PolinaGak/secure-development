import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def create_test_user():
    r = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )
    return r.json()


@pytest.mark.parametrize(
    "email,password",
    [
        ("nonexistent@example.com", "TestPassword123"),
        ("test@example.com", "WrongPassword123"),
    ],
)
def test_invalid_credentials_unified_response(create_test_user, email, password):
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 401
    assert r.json()["detail"] == "Неверное имя пользователя или пароль"
