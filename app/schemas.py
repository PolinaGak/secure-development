from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class WishlistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True


class WishlistSummary(BaseModel):
    id: int
    name: str
    is_public: bool
    created_at: datetime

    class Config:
        orm_mode = True


class WishlistResponse(WishlistCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class WishItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    url: Optional[str] = None
    category: Optional[str] = None


class WishItemResponse(WishItemCreate):
    id: int
    is_reserved: bool
    reserved_by_user_id: Optional[int]
    reservation_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DeleteResponse(BaseModel):
    detail: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int


class ReserveRequest(BaseModel):
    message: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
