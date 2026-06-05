from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.budget import Budget

class BudgetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: int, month: int, year: int) -> list[Budget]:
        result = await self.db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.month == month,
                Budget.year == year,
            )
        )
        return list(result.scalars().all())

    async def get_by_id(self, budget_id: int, user_id: int) -> Budget | None:
        result = await self.db.execute(
            select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_existing(self, user_id: int, category_id: int | None, month: int, year: int) -> Budget | None:
        result = await self.db.execute(
            select(Budget).where(
                and_(
                    Budget.user_id == user_id,
                    Budget.category_id == category_id,
                    Budget.month == month,
                    Budget.year == year,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, data: dict) -> Budget:
        budget = Budget(user_id=user_id, **data)
        self.db.add(budget)
        await self.db.commit()
        await self.db.refresh(budget)
        return budget

    async def update(self, budget: Budget, data: dict) -> Budget:
        for key, value in data.items():
            setattr(budget, key, value)
        await self.db.commit()
        await self.db.refresh(budget)
        return budget

    async def delete(self, budget: Budget):
        await self.db.delete(budget)
        await self.db.commit()