import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def create_test_user():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPassword123",
    }
    client.post("/auth/register", json=user_data)
    return user_data


@pytest.mark.parametrize(
    "email,password",
    [
        ("nonexistent@example.com", "TestPassword123"),  # nonexistent email
        ("testuser@example.com", "WrongPassword123"),  # wrong password
    ],
)
def test_invalid_credentials_unified_response(create_test_user, email, password):
    response = client.post("/auth/login", json={"email": email, "password": password})

    assert response.status_code == 401
    assert response.json() == {"error": "invalid_credentials"}
