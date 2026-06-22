from datetime import UTC, datetime
from typing import Optional

from services.auth import HashedPassword
from sqlmodel import Field, Relationship, SQLModel

from app.models.order import Order


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    password: HashedPassword = Field(nullable=False)
    role: str
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )

    orders: list["Order"] = Relationship(back_populates="user")
