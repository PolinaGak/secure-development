from datetime import datetime, timedelta, timezone
from typing import Dict

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.config import settings
from app.database import _DB
from app.exceptions import ProblemDetail
from app.models import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: Dict, expires_delta: timedelta | None = None) -> str:
    """Создаёт JWT-токен с истечением срока действия"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    """Декодирует JWT и возвращает user_id"""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ProblemDetail(
                title="Invalid Token",
                detail="Токен не содержит идентификатор пользователя",
                status=401,
            )
        return int(user_id)
    except JWTError:
        raise ProblemDetail(
            title="Invalid Token",
            detail="Недействительный или истёкший токен",
            status=401,
        )


@router.post("/register", response_model=Dict)
def register(user: UserCreate):
    """Регистрация нового пользователя"""
    # Проверка на дублирование
    for existing in _DB["users"].values():
        if existing["username"] == user.username:
            raise ProblemDetail(
                title="Username Exists",
                detail="Имя пользователя уже занято",
                status=400,
            )
        if existing["email"] == user.email:
            raise ProblemDetail(
                title="Email Exists", detail="Email уже зарегистрирован", status=400
            )

    new_id = _DB["next_user_id"]
    _DB["users"][new_id] = {
        "id": new_id,
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "created_at": datetime.now(timezone.utc),
        "wishlists": [],
    }
    _DB["next_user_id"] += 1

    return {"id": new_id, "message": "Пользователь создан"}


@router.post("/login", response_model=Dict)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Аутентификация пользователя"""
    user = None
    for u in _DB["users"].values():
        if u["username"] == form_data.username:
            user = u
            break

    if not user or user["password"] != form_data.password:
        raise ProblemDetail(
            title="Invalid Credentials",
            detail="Неверное имя пользователя или пароль",
            status=401,
        )

    access_token = create_access_token(data={"sub": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=Dict)
def get_me(current_user: int = Depends(get_current_user)):
    """Получить данные текущего пользователя"""
    user = _DB["users"].get(current_user)
    if not user:
        raise ProblemDetail(
            title="User Not Found", detail="Пользователь не найден", status=404
        )
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
    }
