from __future__ import annotations

from datetime import date
from decimal import Decimal
from pydantic import BaseModel, field_validator

class BudgetCreate(BaseModel):
    category_id: int | None = None
    amount: Decimal
    month: int
    year: int

    @field_validator("amount")
    @classmethod
    def positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be positive")
        return v

    @field_validator("month")
    @classmethod
    def valid_month(cls, v):
        if not 1 <= v <= 12:
            raise ValueError("month must be 1-12")
        return v

class BudgetUpdate(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = None
    month: int | None = None
    year: int | None = None

    @field_validator("amount")
    @classmethod
    def positive_optional(cls, v):
        if v is not None and v <= 0:
            raise ValueError("amount must be positive")
        return v

    @field_validator("month")
    @classmethod
    def valid_month_optional(cls, v):
        if v is not None and not 1 <= v <= 12:
            raise ValueError("month must be 1-12")
        return v

class BudgetResponse(BaseModel):
    id: int
    category_id: int | None
    amount: Decimal
    month: int
    year: int
    spent: Decimal = Decimal("0")
    remaining: Decimal = Decimal("0")
    percentage_used: float = 0.0
    model_config = {"from_attributes": True}