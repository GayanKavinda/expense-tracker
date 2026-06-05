from decimal import Decimal
from pydantic import BaseModel

class CategorySpend(BaseModel):
    category_id: int | None
    category_name: str | None
    total: Decimal
    percentage: float
    count: int

class DailySpend(BaseModel):
    date: str
    total: Decimal
    count: int

class MonthlySummary(BaseModel):
    month: int
    year: int
    total_spent: Decimal
    total_budgeted: Decimal
    remaining_budget: Decimal
    expense_count: int
    top_category: str | None
    by_category: list[CategorySpend]
    daily_breakdown: list[DailySpend]

class TrendPoint(BaseModel):
    month: int
    year: int
    total: Decimal
    expense_count: int

class InsightsSummary(BaseModel):
    current_month: MonthlySummary
    trend: list[TrendPoint]  # last 6 months