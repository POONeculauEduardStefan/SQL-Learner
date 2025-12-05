# schemas/common.py
from typing import Generic, TypeVar
from pydantic import BaseModel, Field
from typing import List

T = TypeVar("T")


class Meta(BaseModel):
    request_id: str | None = None
    pagination: dict | None = None


class ErrorItem(BaseModel):
    code: str = Field(description="Cod intern de eroare")
    message: str
    details: dict | None = None


class BaseResponse(BaseModel):
    success: bool
    meta: Meta | None = None


class SuccessResponse(BaseResponse, Generic[T]):
    data: T | None = None


class ErrorResponse(BaseResponse):
    error: ErrorItem