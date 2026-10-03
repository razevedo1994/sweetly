from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel


class Status(str, Enum):
    PENDING = "pending"
    IN_PREPARATION = "in_preparation"
    READY = "ready"
    DELIVERED = "delivered"


class OrderResponse(BaseModel):
    customer_name: str
    status: Literal[Status.PENDING]
    total_price: Decimal
    created_by_id: int
    created_at: datetime
    updated_at: datetime
