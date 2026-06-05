from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.category import Category
from sqlalchemy import select

DEFAULT_CATEGORIES = [
    {"name": "Food & Dining", "color": "#f59e0b", "icon": "utensils"},
    {"name": "Transport", "color": "#3b82f6", "icon": "car"},
    {"name": "Shopping", "color": "#8b5cf6", "icon": "shopping-bag"},
    {"name": "Health", "color": "#10b981", "icon": "heart"},
    {"name": "Entertainment", "color": "#ef4444", "icon": "film"},
    {"name": "Utilities", "color": "#6b7280", "icon": "zap"},
    {"name": "Other", "color": "#6366f1", "icon": "tag"},
]

async def seed_default_categories(user_id: int, db: AsyncSession):
    for cat_data in DEFAULT_CATEGORIES:
        exists = await db.execute(
            select(Category).where(Category.user_id == user_id, Category.name == cat_data["name"])
        )
        if not exists.scalar_one_or_none():
            db.add(Category(user_id=user_id, is_default=True, **cat_data))
    await db.commit()