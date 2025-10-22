"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db
from app.exceptions import InvalidCredentials
from app.hashing import verify_password

auth_router = APIRouter()


@auth_router.post(
    "/auth/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, user_data)
    except HTTPException as e:
        raise e
    return user


@auth_router.post("/auth/login", response_model=schemas.TokenResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise InvalidCredentials()

    return {
        "access_token": f"fake-jwt-token-for-user-{user.id}",
        "token_type": "bearer",
        "user_id": user.id,
    }

"""
