from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    id: int
    updated_at: datetime
    created_at: datetime
