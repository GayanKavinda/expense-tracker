from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category

class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: int) -> list[Category]:
        result = await self.db.execute(
            select(Category).where(Category.user_id == user_id).order_by(Category.name)
        )
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int, user_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id, Category.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, user_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.name == name, Category.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, name: str, color: str, icon: str) -> Category:
        cat = Category(user_id=user_id, name=name, color=color, icon=icon)
        self.db.add(cat)
        await self.db.commit()
        await self.db.refresh(cat)
        return cat

    async def update(self, category: Category, data: dict) -> Category:
        for key, value in data.items():
            if value is not None:
                setattr(category, key, value)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category):
        await self.db.delete(category)
        await self.db.commit()