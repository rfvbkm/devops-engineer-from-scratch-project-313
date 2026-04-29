from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, func
from sqlmodel import Field, SQLModel


class Link(SQLModel, table=True):
    __tablename__ = "links"

    id: Optional[int] = Field(default=None, primary_key=True)
    original_url: str = Field(sa_column=Column(String, nullable=False))
    short_name: str = Field(
        sa_column=Column(String, nullable=False, unique=True),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
