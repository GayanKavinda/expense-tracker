from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.expense import Expense

class ExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        category_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        search: str | None = None,
    ) -> tuple[list[Expense], int]:
        filters = [Expense.user_id == user_id]

        if category_id:
            filters.append(Expense.category_id == category_id)
        if start_date:
            filters.append(Expense.date >= start_date)
        if end_date:
            filters.append(Expense.date <= end_date)
        if min_amount:
            filters.append(Expense.amount >= min_amount)
        if max_amount:
            filters.append(Expense.amount <= max_amount)
        if search:
            filters.append(Expense.description.ilike(f"%{search}%"))

        count_result = await self.db.execute(
            select(func.count()).select_from(Expense).where(and_(*filters))
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Expense)
            .where(and_(*filters))
            .order_by(Expense.date.desc(), Expense.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, expense_id: int, user_id: int) -> Expense | None:
        result = await self.db.execute(
            select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, data: dict) -> Expense:
        expense = Expense(user_id=user_id, **data)
        self.db.add(expense)
        await self.db.commit()
        await self.db.refresh(expense)
        return expense

    async def update(self, expense: Expense, data: dict) -> Expense:
        for key, value in data.items():
            setattr(expense, key, value)
        await self.db.commit()
        await self.db.refresh(expense)
        return expense

    async def delete(self, expense: Expense):
        await self.db.delete(expense)
        await self.db.commit()