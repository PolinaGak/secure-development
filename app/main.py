from typing import Dict, List

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth import router
from app.database import _DB
from app.exceptions import InvalidCredentials, ProblemDetail
from app.logging_config import setup_logging
from app.models import (
    ReserveRequest,
    UserCreate,
    WishItemCreate,
    WishItemResponse,
    WishlistCreate,
    now_utc,
)

setup_logging()

app = FastAPI(
    title="Wishlist API", description="API для управления вишлистами", version="1.0.0"
)
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/wishlists/{wishlist_id}/items", response_model=List[WishItemResponse])
def get_wishlist_items(wishlist_id: int):
    if wishlist_id not in _DB["wishlists"]:
        raise ProblemDetail(
            title="Wishlist Not Found", detail="Вишлист не найден", status=404
        )
    return list(_DB["wishlists"][wishlist_id]["items"].values())


@app.post("/wishlists/{wishlist_id}/items", response_model=WishItemResponse)
def add_to_wishlist(wishlist_id: int, item: WishItemCreate):
    if wishlist_id not in _DB["wishlists"]:
        raise ProblemDetail(
            title="Wishlist Not Found", detail="Вишлист не найден", status=404
        )
    new_id = _DB["next_item_id"]
    now = now_utc()
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
    for wishlist_id, wishlist in _DB["wishlists"].items():
        if item_id in wishlist["items"]:
            return wishlist["items"][item_id]
    raise ProblemDetail(title="Item Not Found", detail="Элемент не найден", status=404)


@app.post("/wishlists", response_model=Dict)
def create_wishlist(wishlist: WishlistCreate, user_id: int):
    if user_id not in _DB["users"]:
        raise ProblemDetail(
            title="User Not Found", detail="Пользователь не найден", status=404
        )
    new_id = _DB["next_wishlist_id"]
    _DB["wishlists"][new_id] = {
        **wishlist.model_dump(),
        "id": new_id,
        "owner_id": user_id,
        "items": {},
        "created_at": now_utc(),
    }
    _DB["next_wishlist_id"] += 1
    return {"id": new_id, "message": "Вишлист создан"}


@app.put("/wishlists/{wishlist_id}/items/{item_id}", response_model=WishItemResponse)
def update_wishlist_item(wishlist_id: int, item_id: int, item_update: WishItemCreate):
    if (
        wishlist_id not in _DB["wishlists"]
        or item_id not in _DB["wishlists"][wishlist_id]["items"]
    ):
        raise ProblemDetail(
            title="Item Not Found", detail="Элемент не найден", status=404
        )
    item = _DB["wishlists"][wishlist_id]["items"][item_id]
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        item[field] = value
    item["updated_at"] = now_utc()
    return item


@app.get("/users/{user_id}/wishlists/{wishlist_id}", response_model=Dict)
def get_user_wishlist(user_id: int, wishlist_id: int):
    if user_id not in _DB["users"]:
        raise ProblemDetail(
            title="User Not Found", detail="Пользователь не найден", status=404
        )
    if wishlist_id not in _DB["wishlists"]:
        raise ProblemDetail(
            title="Wishlist Not Found", detail="Вишлист не найден", status=404
        )
    wishlist = _DB["wishlists"][wishlist_id]
    if wishlist["owner_id"] != user_id:
        raise ProblemDetail(
            title="Access Denied",
            detail="Вишлист не принадлежит пользователю",
            status=403,
        )
    return wishlist


@app.put(
    "/wishlists/{wishlist_id}/items/{item_id}/reserve", response_model=WishItemResponse
)
def reserve_item(wishlist_id: int, item_id: int, reserve_request: ReserveRequest):
    if (
        wishlist_id not in _DB["wishlists"]
        or item_id not in _DB["wishlists"][wishlist_id]["items"]
    ):
        raise ProblemDetail(
            title="Item Not Found", detail="Элемент не найден", status=404
        )
    item = _DB["wishlists"][wishlist_id]["items"][item_id]
    if item["is_reserved"]:
        raise ProblemDetail(
            title="Already Reserved", detail="Элемент уже зарезервирован", status=400
        )
    item["is_reserved"] = True
    item["reserved_by"] = reserve_request.reserved_by
    item["reserved_at"] = now_utc()
    item["reservation_message"] = reserve_request.message
    item["updated_at"] = now_utc()
    return item


@app.put(
    "/wishlists/{wishlist_id}/items/{item_id}/unreserve",
    response_model=WishItemResponse,
)
def unreserve_item(wishlist_id: int, item_id: int):
    if (
        wishlist_id not in _DB["wishlists"]
        or item_id not in _DB["wishlists"][wishlist_id]["items"]
    ):
        raise ProblemDetail(
            title="Item Not Found", detail="Элемент не найден", status=404
        )
    item = _DB["wishlists"][wishlist_id]["items"][item_id]
    if not item["is_reserved"]:
        raise ProblemDetail(
            title="Not Reserved", detail="Элемент не был зарезервирован", status=400
        )
    item["is_reserved"] = False
    item["reserved_by"] = None
    item["reserved_at"] = None
    item["reservation_message"] = None
    item["updated_at"] = now_utc()
    return item


@app.post("/users", response_model=Dict)
def create_user(user: UserCreate):
    for existing_user in _DB["users"].values():
        if existing_user["username"] == user.username:
            raise ProblemDetail(
                title="Username Exists",
                detail="Имя пользователя уже занято",
                status=400,
            )
        if existing_user["email"] == user.email:
            raise ProblemDetail(
                title="Email Exists", detail="Email уже зарегистрирован", status=400
            )
    new_id = _DB["next_user_id"]
    _DB["users"][new_id] = {
        **user.model_dump(),
        "id": new_id,
        "created_at": now_utc(),
        "wishlists": [],
    }
    _DB["next_user_id"] += 1
    return {"id": new_id, "message": "Пользователь создан"}


@app.get("/users/{user_id}/wishlists", response_model=List[Dict])
def get_user_wishlists(user_id: int):
    if user_id not in _DB["users"]:
        raise ProblemDetail(
            title="User Not Found", detail="Пользователь не найден", status=404
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
    if (
        wishlist_id not in _DB["wishlists"]
        or item_id not in _DB["wishlists"][wishlist_id]["items"]
    ):
        raise ProblemDetail(
            title="Item Not Found", detail="Элемент не найден", status=404
        )
    deleted_item = _DB["wishlists"][wishlist_id]["items"].pop(item_id)
    return {"message": f"Элемент '{deleted_item['name']}' удален из вишлиста"}


@app.delete("/wishlists/{wishlist_id}")
def delete_wishlist(wishlist_id: int):
    if wishlist_id not in _DB["wishlists"]:
        raise ProblemDetail(
            title="Wishlist Not Found", detail="Вишлист не найден", status=404
        )
    deleted_wishlist = _DB["wishlists"].pop(wishlist_id)
    return {"message": f"Вишлист '{deleted_wishlist['name']}' удален"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in _DB["users"]:
        raise ProblemDetail(
            title="User Not Found", detail="Пользователь не найден", status=404
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return ProblemDetail(
        title="Validation Error",
        detail="Ошибка валидации входных данных",
        status=422,
    ).to_response(request)


@app.exception_handler(InvalidCredentials)
async def handle_invalid_credentials(request: Request, exc: InvalidCredentials):
    return JSONResponse(status_code=401, content={"error": "invalid_credentials"})



@app.exception_handler(ProblemDetail)
async def problem_detail_handler(request: Request, exc: ProblemDetail):
    return exc.to_response(request)