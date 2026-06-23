from datetime import UTC, datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.product import Product
from app.models.user import User


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str = Field(nullable=False)
    status: str = Field(nullable=False)
    total_price: Decimal = Field(nullable=False)
    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )

    user: Optional[User] = Relationship(back_populates="orders")
    order_items: list["OrderItems"] = Relationship(back_populates="order")


class OrderItems(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    product_id: Optional[int] = Field(
        default=None, foreign_key="product.id", nullable=True
    )
    product_name_snapshot: str = Field(nullable=False)
    unit_price_snapshot: Decimal = Field(nullable=False)
    quantity: int = Field(ge=1, nullable=False)

    order: Optional[Order] = Relationship(back_populates="order_items")
    products: list["Product"] = Relationship(back_populates="orders")
