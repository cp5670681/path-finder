from typing import Any, Generic, TypeVar
from pydantic import BaseModel

DataType = TypeVar("DataType")
T = TypeVar("T")

class IResponseBase(BaseModel, Generic[T]):
    message: str = ""
    meta: dict | Any | None = {}
    data: T | None = None


class IGetResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data got correctly"


class IPostResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data created correctly"


class IPutResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data updated correctly"


class IDeleteResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data deleted correctly"


def create_response(
    data: DataType,
    message: str | None = None,
    meta: dict | Any | None = {},
) -> (
    IResponseBase[DataType]
    | IGetResponseBase[DataType]
    | IPutResponseBase[DataType]
    | IDeleteResponseBase[DataType]
    | IPostResponseBase[DataType]
):
    if message is None:
        return {"data": data, "meta": meta}
    return {"data": data, "message": message, "meta": meta}
