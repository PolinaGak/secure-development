from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, constr

app = FastAPI(
    title="Wishlist API", description="API для управления вишлистами", version="1.0.0"
)


class WishItemCreate(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = None
    url: Optional[str] = None
    category: Optional[str] = None


class WishItemResponse(WishItemCreate):
    id: int
    is_reserved: bool = False
    reserved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReserveRequest(BaseModel):
    reserved_by: constr(min_length=1, max_length=50)
    message: Optional[str] = None


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr


class WishlistCreate(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: bool = True


_DB = {
    "users": {},
    "wishlists": {},
    "next_user_id": 1,
    "next_wishlist_id": 1,
    "next_item_id": 1,
}


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "Wishlist API"}


@app.get("/wishlists/{wishlist_id}/items", response_model=List[WishItemResponse])
def get_wishlist_items(wishlist_id: int):
    """Получить все элементы вишлиста"""
    if wishlist_id not in _DB["wishlists"]:
        raise ApiError(
            code="wishlist_not_found", message="Вишлист не найден", status=404
        )
    return list(_DB["wishlists"][wishlist_id]["items"].values())


@app.post("/wishlists/{wishlist_id}/items", response_model=WishItemResponse)
def add_to_wishlist(wishlist_id: int, item: WishItemCreate):
    """Добавить новый элемент в вишлист"""
    if wishlist_id not in _DB["wishlists"]:
        raise ApiError(
            code="wishlist_not_found", message="Вишлист не найден", status=404
        )

    new_id = _DB["next_item_id"]
    now = datetime.now()

    wishlist_item = {
        "id": new_id,
        **item.model_dump(),
        "is_reserved": False,
        "reserved_by": None,
        "created_at": now,
        "updated_at": now,
    }

    _DB["wishlists"][wishlist_id]["items"][new_id] = wishlist_item
    _DB["next_item_id"] += 1

    return wishlist_item


@app.get("/wishlist/{item_id}", response_model=WishItemResponse)
def get_wishlist_item(item_id: int):
    """Получить элемент вишлиста по ID"""
    for wishlist_id, wishlist in _DB["wishlists"].items():
        if item_id in wishlist["items"]:
            return wishlist["items"][item_id]

    raise ApiError(code="not_found", message="Элемент не найден", status=404)


@app.post("/wishlists", response_model=Dict)
def create_wishlist(wishlist: WishlistCreate, user_id: int):
    """Создать новый вишлист"""
    if user_id not in _DB["users"]:
        raise ApiError(
            code="user_not_found", message="Пользователь не найден", status=404
        )

    new_id = _DB["next_wishlist_id"]
    _DB["wishlists"][new_id] = {
        **wishlist.model_dump(),
        "id": new_id,
        "owner_id": user_id,
        "items": {},
        "created_at": datetime.now(),
    }
    _DB["next_wishlist_id"] += 1

    return {"id": new_id, "message": "Вишлист создан"}


@app.put("/wishlists/{wishlist_id}/items/{item_id}", response_model=WishItemResponse)
def update_wishlist_item(wishlist_id: int, item_id: int, item_update: WishItemCreate):
    """Обновить элемент вишлиста"""
    if (
        wishlist_id not in _DB["wishlists"]
        or item_id not in _DB["wishlists"][wishlist_id]["items"]
    ):
        raise ApiError(code="item_not_found", message="Элемент не найден", status=404)

    item = _DB["wishlists"][wishlist_id]["items"][item_id]
    update_data = item_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        item[field] = value
    item["updated_at"] = datetime.now()

    return item


@app.get("/users/{user_id}/wishlists/{wishlist_id}", response_model=Dict)
def get_user_wishlist(user_id: int, wishlist_id: int):
    """Получить вишлист по юзеру по ID"""
    if user_id not in _DB["users"]:
        raise ApiError(
            code="user_not_found", message="Пользователь не найден", status=404
        )

    if wishlist_id not in _DB["wishlists"]:
        raise ApiError(
            code="wishlist_not_found", message="Вишлист не найден", status=404
        )

    wishlist = _DB["wishlists"][wishlist_id]

    if wishlist["owner_id"] != user_id:
        raise ApiError(
            code="access_denied",
            message="Вишлист не принадлежит пользователю",
            status=403,
        )

    return wishlist


@app.put(
    "/wishlists/{wishlist_id}/items/{item_id}/reserve", response_model=WishItemResponse
)
def reserve_item(wishlist_id: int, item_id: int, reserve_request: ReserveRequest):
    """Зарезервировать элемент вишлиста"""
    if (
        wishlist_id not in _DB["wishlists"]
        or item_id not in _DB["wishlists"][wishlist_id]["items"]
    ):
        raise ApiError(code="item_not_found", message="Элемент не найден", status=404)

    item = _DB["wishlists"][wishlist_id]["items"][item_id]

    if item["is_reserved"]:
        raise ApiError(
            code="already_reserved", message="Элемент уже зарезервирован", status=400
        )

    item["is_reserved"] = True
    item["reserved_by"] = reserve_request.reserved_by
    item["reserved_at"] = datetime.now()
    item["reservation_message"] = reserve_request.message
    item["updated_at"] = datetime.now()

    return item


@app.put(
    "/wishlists/{wishlist_id}/items/{item_id}/unreserve",
    response_model=WishItemResponse,
)
def unreserve_item(wishlist_id: int, item_id: int):
    """Снять резервацию с элемента"""
    if (
        wishlist_id not in _DB["wishlists"]
        or item_id not in _DB["wishlists"][wishlist_id]["items"]
    ):
        raise ApiError(code="item_not_found", message="Элемент не найден", status=404)

    item = _DB["wishlists"][wishlist_id]["items"][item_id]

    if not item["is_reserved"]:
        raise ApiError(
            code="not_reserved", message="Элемент не был зарезервирован", status=400
        )

    item["is_reserved"] = False
    item["reserved_by"] = None
    item["reserved_at"] = None
    item["reservation_message"] = None
    item["updated_at"] = datetime.now()

    return item


@app.post("/users", response_model=Dict)
def create_user(user: UserCreate):
    """Создать нового пользователя"""
    for existing_user in _DB["users"].values():
        if existing_user["username"] == user.username:
            raise ApiError(
                code="username_exists",
                message="Имя пользователя уже занято",
                status=400,
            )
        if existing_user["email"] == user.email:
            raise ApiError(
                code="email_exists", message="Email уже зарегистрирован", status=400
            )

    new_id = _DB["next_user_id"]
    _DB["users"][new_id] = {
        **user.model_dump(),
        "id": new_id,
        "created_at": datetime.now(),
        "wishlists": [],
    }
    _DB["next_user_id"] += 1

    return {"id": new_id, "message": "Пользователь создан"}


@app.get("/users/{user_id}/wishlists", response_model=List[Dict])
def get_user_wishlists(user_id: int):
    """Получить все вишлисты пользователя"""
    if user_id not in _DB["users"]:
        raise ApiError(
            code="user_not_found", message="Пользователь не найден", status=404
        )

    user_wishlists = []
    for wishlist_id, wishlist in _DB["wishlists"].items():
        if wishlist["owner_id"] == user_id:
            wishlist_summary = {
                "id": wishlist["id"],
                "name": wishlist["name"],
                "description": wishlist["description"],
                "item_count": len(wishlist["items"]),
                "is_public": wishlist["is_public"],
            }
            user_wishlists.append(wishlist_summary)

    return user_wishlists


@app.delete("/wishlists/{wishlist_id}/items/{item_id}")
def delete_wishlist_item(wishlist_id: int, item_id: int):
    """Удалить элемент из вишлиста"""
    if (
        wishlist_id not in _DB["wishlists"]
        or item_id not in _DB["wishlists"][wishlist_id]["items"]
    ):
        raise ApiError(code="item_not_found", message="Элемент не найден", status=404)

    deleted_item = _DB["wishlists"][wishlist_id]["items"].pop(item_id)
    return {"message": f"Элемент '{deleted_item['name']}' удален из вишлиста"}


@app.delete("/wishlists/{wishlist_id}")
def delete_wishlist(wishlist_id: int):
    """Удалить вишлист"""
    if wishlist_id not in _DB["wishlists"]:
        raise ApiError(
            code="wishlist_not_found", message="Вишлист не найден", status=404
        )

    deleted_wishlist = _DB["wishlists"].pop(wishlist_id)
    return {"message": f"Вишлист '{deleted_wishlist['name']}' удален"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Удалить пользователя"""
    if user_id not in _DB["users"]:
        raise ApiError(
            code="user_not_found", message="Пользователь не найден", status=404
        )

    wishlists_to_delete = [
        wishlist_id
        for wishlist_id, wishlist in _DB["wishlists"].items()
        if wishlist["owner_id"] == user_id
    ]

    for wishlist_id in wishlists_to_delete:
        _DB["wishlists"].pop(wishlist_id)

    deleted_user = _DB["users"].pop(user_id)
    return {
        "message": f"Пользователь '{deleted_user['username']}' и все его вишлисты удалены"
    }
