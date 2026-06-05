from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repo = CategoryRepository(db)

    async def get_all(self, user_id: int):
        return await self.repo.get_all(user_id)

    async def create(self, user_id: int, data: CategoryCreate):
        existing = await self.repo.get_by_name(data.name, user_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists")
        return await self.repo.create(user_id, data.name, data.color, data.icon)

    async def update(self, category_id: int, user_id: int, data: CategoryUpdate):
        cat = await self.repo.get_by_id(category_id, user_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        if cat.is_default:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit default category")
        return await self.repo.update(cat, data.model_dump(exclude_none=True))

    async def delete(self, category_id: int, user_id: int):
        cat = await self.repo.get_by_id(category_id, user_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        if cat.is_default:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete default category")
        await self.repo.delete(cat)