from typing import Generic, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")

class ResponseOK(BaseModel, Generic[T]):
    status: str = "ok"
    data: T

class ResponseError(BaseModel):
    status: str = "error"
    message: str
    details: Any | None = None
    
class PaginatedResponse(BaseModel, Generic[T]):
    status: str = "ok"
    total: int
    limit: int
    offset: int
    data: list[T] 