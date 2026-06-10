from pydantic import BaseModel
from enum import Enum
from decimal import Decimal
from datetime import datetime


class Status(str, Enum):
    PENDING = "pending"
    IN_PREPARATION = "in_preparation"
    READY = "ready"
    DELIVERED = "delivered"


class OrderResponse(BaseModel):
    customer_name: str
    status: Status.PENDING
    total_price: Decimal
    created_by_id: int
    created_at: datetime
    updated_at: datetime
