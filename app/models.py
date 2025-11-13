from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, StringConstraints, field_validator


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


SafeString = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=100,
        strip_whitespace=True,
    ),
]

SafeShortString = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=50,
        strip_whitespace=True,
    ),
]

UsernameString = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=50,
        strip_whitespace=True,
    ),
]

PasswordString = Annotated[
    str,
    StringConstraints(
        min_length=6,
        max_length=100,
        strip_whitespace=True,
    ),
]


class WishItemCreate(BaseModel):
    name: SafeString
    description: Optional[str] = None
    price: Optional[Decimal] = None
    url: Optional[str] = None
    category: Optional[str] = None

    @field_validator("name", "description", "url", "category")
    def block_script_tags(cls, v: Optional[str]) -> Optional[str]:
        if v and "<script" in v.lower():
            raise ValueError("Скрипты запрещены")
        return v

    @field_validator("price")
    def price_must_be_non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("Цена не может быть отрицательной")
        return v


class WishItemResponse(WishItemCreate):
    id: int
    is_reserved: bool = False
    reserved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReserveRequest(BaseModel):
    reserved_by: SafeShortString
    message: Optional[str] = None


class UserCreate(BaseModel):
    username: UsernameString
    email: EmailStr
    password: PasswordString


class WishlistCreate(BaseModel):
    name: SafeString
    description: Optional[str] = None
    is_public: bool = True
