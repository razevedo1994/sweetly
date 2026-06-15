from datetime import UTC, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class category(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )
