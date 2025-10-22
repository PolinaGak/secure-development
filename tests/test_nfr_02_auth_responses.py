import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.fixture
def create_test_user():
    # Генерируем уникальный email для каждого запуска
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "TestPassword123",
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    return user_data

@pytest.mark.parametrize(
    "email,password",
    [
        ("nonexistent@example.com", "TestPassword123"),  # nonexistent email
        ("testuser_12345@example.com", "WrongPassword123"),  # wrong password (email не существует)
    ],
)
def test_invalid_credentials_unified_response(email, password):
    """Тест без фикстуры — проверяем несуществующие данные"""
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401
    assert response.json() == {"error": "invalid_credentials"}

def test_login_with_created_user(create_test_user):
    """Тест с корректным логином"""
    user = create_test_user
    response = client.post("/auth/login", json={
        "email": user["email"],
        "password": user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
