from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseORMSchema(BaseModel):
    model_config = {"from_attributes": True}

class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list
