from pydantic import BaseModel, field_validator
import re

class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"
    icon: str = "tag"

    @field_validator("color")
    @classmethod
    def valid_hex(cls, v):
        if not re.match(r"^#[0-9a-fA-F]{6}$", v):
            raise ValueError("color must be valid hex e.g. #ff0000")
        return v

class CategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None

    @field_validator("color")
    @classmethod
    def valid_hex(cls, v):
        if v and not re.match(r"^#[0-9a-fA-F]{6}$", v):
            raise ValueError("color must be valid hex e.g. #ff0000")
        return v

class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    icon: str
    is_default: bool
    model_config = {"from_attributes": True}