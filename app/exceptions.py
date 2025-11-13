from typing import Optional
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse


class InvalidCredentials(Exception):
    """Исключение для неверных учетных данных (унифицированный ответ)"""

    pass


class ProblemDetail(Exception):
    """
    RFC 7807 Problem Details
    """

    def __init__(
        self,
        *,
        title: str,
        detail: str,
        status: int = 400,
        type: Optional[str] = None,
        instance: Optional[str] = None,
    ):
        self.title = title
        self.detail = detail
        self.status = status
        self.type = (
            type or f"https://api.wishlist.com/errors/{title.lower().replace(' ', '-')}"
        )
        self.instance = instance
        self.correlation_id = str(uuid4())

    def to_response(self, request: Request) -> JSONResponse:
        content = {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance or str(request.url),
            "correlation_id": self.correlation_id,
        }
        return JSONResponse(
            status_code=self.status,
            content=content,
            headers={"X-Correlation-ID": self.correlation_id},
        )