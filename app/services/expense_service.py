import math
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.expense_repo import ExpenseRepository
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

class ExpenseService:
    def __init__(self, db: AsyncSession):
        self.repo = ExpenseRepository(db)

    async def get_all(
        self,
        user_id: int,
        page: int,
        page_size: int,
        category_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        search: str | None = None,
    ):
        items, total = await self.repo.get_all(
            user_id, page, page_size,
            category_id, start_date, end_date,
            min_amount, max_amount, search,
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total else 0,
        }

    async def get_one(self, expense_id: int, user_id: int):
        expense = await self.repo.get_by_id(expense_id, user_id)
        if not expense:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        return expense

    async def create(self, user_id: int, data: ExpenseCreate):
        return await self.repo.create(user_id, data.model_dump())

    async def update(self, expense_id: int, user_id: int, data: ExpenseUpdate):
        expense = await self.repo.get_by_id(expense_id, user_id)
        if not expense:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        return await self.repo.update(expense, data.model_dump(exclude_none=True))

    async def delete(self, expense_id: int, user_id: int):
        expense = await self.repo.get_by_id(expense_id, user_id)
        if not expense:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        await self.repo.delete(expense)