from datetime import UTC, datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.product import Product


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )

    products: list["Product"] = Relationship(back_populates="category")
