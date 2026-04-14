from pydantic import BaseModel, Field


class LinkCreate(BaseModel):
    original_url: str = Field(min_length=1)
    short_name: str = Field(min_length=1)


class LinkUpdate(BaseModel):
    original_url: str = Field(min_length=1)
    short_name: str = Field(min_length=1)


class LinkRead(BaseModel):
    id: int
    original_url: str
    short_name: str
    short_url: str
