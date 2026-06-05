from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.repositories.budget_repo import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetUpdate

class BudgetService:
    def __init__(self, db: AsyncSession):
        self.repo = BudgetRepository(db)
        self.db = db

    async def _get_spent(self, user_id: int, category_id: int | None, month: int, year: int) -> Decimal:
        filters = [
            Expense.user_id == user_id,
            func.extract("month", Expense.date) == month,
            func.extract("year", Expense.date) == year,
        ]
        if category_id is not None:
            filters.append(Expense.category_id == category_id)

        result = await self.db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(and_(*filters))
        )
        return Decimal(str(result.scalar_one()))

    async def _enrich(self, budget) -> dict:
        spent = await self._get_spent(budget.user_id, budget.category_id, budget.month, budget.year)
        amount = Decimal(str(budget.amount))
        remaining = amount - spent
        percentage = float((spent / amount * 100).quantize(Decimal("0.01"))) if amount else 0.0
        return {
            "id": budget.id,
            "category_id": budget.category_id,
            "amount": amount,
            "month": budget.month,
            "year": budget.year,
            "spent": spent,
            "remaining": remaining,
            "percentage_used": percentage,
        }

    async def get_all(self, user_id: int, month: int, year: int):
        budgets = await self.repo.get_all(user_id, month, year)
        return [await self._enrich(b) for b in budgets]

    async def create(self, user_id: int, data: BudgetCreate):
        existing = await self.repo.get_existing(user_id, data.category_id, data.month, data.year)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Budget already exists for this category and period")
        budget = await self.repo.create(user_id, data.model_dump())
        return await self._enrich(budget)

    async def update(self, budget_id: int, user_id: int, data: BudgetUpdate):
        budget = await self.repo.get_by_id(budget_id, user_id)
        if not budget:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
        updated = await self.repo.update(budget, data.model_dump(exclude_none=True))
        return await self._enrich(updated)

    async def delete(self, budget_id: int, user_id: int):
        budget = await self.repo.get_by_id(budget_id, user_id)
        if not budget:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
        await self.repo.delete(budget)