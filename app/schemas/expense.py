from __future__ import annotations

import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator

class ExpenseCreate(BaseModel):
    amount: Decimal
    currency: str = "LKR"
    description: str
    notes: str | None = None
    date: datetime.date
    category_id: int | None = None

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, v):
        if v <= 0:
            raise ValueError("amount must be positive")
        return v

    @field_validator("currency")
    @classmethod
    def valid_currency(cls, v):
        if len(v) != 3:
            raise ValueError("currency must be 3-letter ISO code")
        return v.upper()

class ExpenseUpdate(BaseModel):
    amount: Decimal | None = None
    currency: str | None = None
    description: str | None = None
    notes: str | None = None
    date: datetime.date | None = None
    category_id: int | None = None

class ExpenseResponse(BaseModel):
    id: int
    amount: Decimal
    currency: str
    description: str
    notes: str | None
    date: datetime.date
    category_id: int | None
    model_config = {"from_attributes": True}

class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int