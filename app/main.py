from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.auth import auth_router
from app.db import get_db
from app.deps import get_current_user_id, get_current_user_id_optional
from app.exceptions import ApiError, InvalidCredentials

app = FastAPI(title="Wishlist API", description="API для управления вишлистами", version="1.0.0")

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "Ошибка валидации"}},
    )


@app.exception_handler(InvalidCredentials)
async def handle_invalid_credentials(request: Request, exc: InvalidCredentials):
    return JSONResponse(status_code=401, content={"error": "invalid_credentials"})


@app.post("/users", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.delete("/users/me", response_model=schemas.DeleteResponse)
def delete_own_user(current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return crud.delete_user(db, current_user_id)


@app.post("/wishlists", response_model=schemas.WishlistResponse, status_code=201)
def create_wishlist(
    wishlist: schemas.WishlistCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return crud.create_wishlist(db, wishlist, current_user_id)


@app.get("/wishlists/mine", response_model=List[schemas.WishlistSummary])
def get_my_wishlists(current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return crud.get_user_wishlists(db, current_user_id)


@app.get("/wishlists/{wishlist_id}", response_model=schemas.WishlistResponse)
def get_wishlist(
    wishlist_id: int,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id_optional),
):
    return crud.get_wishlist_public_or_owner(db, wishlist_id, current_user_id)


@app.delete("/wishlists/{wishlist_id}", response_model=schemas.DeleteResponse)
def delete_wishlist(
    wishlist_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    crud.get_user_wishlist(db, current_user_id, wishlist_id)
    return crud.delete_wishlist(db, wishlist_id)


@app.post("/wishlists/{wishlist_id}/items", response_model=schemas.WishItemResponse)
def add_to_wishlist(
    wishlist_id: int,
    item: schemas.WishItemCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    crud.get_user_wishlist(db, current_user_id, wishlist_id)
    return crud.add_item_to_wishlist(db, wishlist_id, item)


@app.get("/wishlists/{wishlist_id}/items", response_model=List[schemas.WishItemResponse])
def get_wishlist_items(
    wishlist_id: int,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_id_optional),
):
    crud.get_wishlist_public_or_owner(db, wishlist_id, current_user_id)
    return crud.get_items_from_wishlist(db, wishlist_id)


@app.get("/wishlists/items/{item_id}", response_model=schemas.WishItemResponse)
def get_wishlist_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_wishlist_item_by_id(db, item_id)
    wishlist = crud.get_wishlist_by_id(db, item.wishlist_id)
    if not wishlist.is_public:
        raise HTTPException(status_code=403, detail="Access to private wishlist denied")
    return item


@app.put("/wishlists/{wishlist_id}/items/{item_id}", response_model=schemas.WishItemResponse)
def update_item(
    wishlist_id: int,
    item_id: int,
    item: schemas.WishItemCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    crud.get_user_wishlist(db, current_user_id, wishlist_id)
    return crud.update_wishlist_item(db, wishlist_id, item_id, item)


@app.put(
    "/wishlists/{wishlist_id}/items/{item_id}/reserve",
    response_model=schemas.WishItemResponse,
)
def reserve_item(
    wishlist_id: int,
    item_id: int,
    reserve: schemas.ReserveRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return crud.reserve_item(db, wishlist_id, item_id, current_user_id, reserve.message)


@app.put(
    "/wishlists/{wishlist_id}/items/{item_id}/unreserve",
    response_model=schemas.WishItemResponse,
)
def unreserve_item(
    wishlist_id: int,
    item_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    crud.get_user_wishlist(db, current_user_id, wishlist_id)
    return crud.unreserve_item(db, wishlist_id, item_id)


@app.delete("/wishlists/{wishlist_id}/items/{item_id}", response_model=schemas.DeleteResponse)
def delete_item(
    wishlist_id: int,
    item_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    crud.get_user_wishlist(db, current_user_id, wishlist_id)
    return crud.delete_item(db, wishlist_id, item_id)
