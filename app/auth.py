from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, constr

from app.database import _DB
from app.exceptions import InvalidCredentials
from app.hashing import hash_password, verify_password

auth_router = APIRouter()


class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@auth_router.post("/auth/register")
def register(data: RegisterRequest):
    for user in _DB["users"].values():
        if user["email"] == data.email:
            raise InvalidCredentials()

    user_id = _DB["next_user_id"]
    _DB["next_user_id"] += 1

    _DB["users"][user_id] = {
        "id": user_id,
        "username": data.username,
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "created_at": datetime.now(),
    }

    return {"id": user_id, "message": "Пользователь зарегистрирован"}


@auth_router.post("/auth/login")
def login(data: LoginRequest):
    user = next((u for u in _DB["users"].values() if u["email"] == data.email), None)
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise InvalidCredentials()
    return {"token": f"fake-token-for-user-{user['id']}"}
