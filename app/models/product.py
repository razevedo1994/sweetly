from datetime import UTC, datetime
from decimal import Decimal
from typing import Optional

from pydantic.main import BaseModel
from sqlalchemy import table
from sqlmodel import Field, Relationship, SQLModel

from app.models.category import Category


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    description: str
    price: Decimal = Field(nullable=False)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    is_available: bool = Field(default=True, nullable=False)
    is_archived: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )

    category: Optional["Category"] = Relationship(back_populates="products")
