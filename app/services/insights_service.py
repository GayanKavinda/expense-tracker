from decimal import Decimal
from datetime import date
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.models.category import Category
from app.models.budget import Budget

class InsightsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _total_spent(self, user_id: int, month: int, year: int) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user_id,
                extract("month", Expense.date) == month,
                extract("year", Expense.date) == year,
            )
        )
        return Decimal(str(result.scalar_one()))

    async def _total_budgeted(self, user_id: int, month: int, year: int) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Budget.amount), 0)).where(
                Budget.user_id == user_id,
                Budget.month == month,
                Budget.year == year,
            )
        )
        return Decimal(str(result.scalar_one()))

    async def _by_category(self, user_id: int, month: int, year: int, total: Decimal) -> list[dict]:
        result = await self.db.execute(
            select(
                Expense.category_id,
                Category.name,
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("count"),
            )
            .outerjoin(Category, Expense.category_id == Category.id)
            .where(
                Expense.user_id == user_id,
                extract("month", Expense.date) == month,
                extract("year", Expense.date) == year,
            )
            .group_by(Expense.category_id, Category.name)
            .order_by(func.sum(Expense.amount).desc())
        )
        rows = result.all()
        out = []
        for row in rows:
            cat_total = Decimal(str(row.total))
            pct = float((cat_total / total * 100).quantize(Decimal("0.01"))) if total else 0.0
            out.append({
                "category_id": row.category_id,
                "category_name": row.name or "Uncategorized",
                "total": cat_total,
                "percentage": pct,
                "count": row.count,
            })
        return out

    async def _daily_breakdown(self, user_id: int, month: int, year: int) -> list[dict]:
        result = await self.db.execute(
            select(
                Expense.date,
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("count"),
            )
            .where(
                Expense.user_id == user_id,
                extract("month", Expense.date) == month,
                extract("year", Expense.date) == year,
            )
            .group_by(Expense.date)
            .order_by(Expense.date)
        )
        return [
            {"date": str(row.date), "total": Decimal(str(row.total)), "count": row.count}
            for row in result.all()
        ]

    async def _expense_count(self, user_id: int, month: int, year: int) -> int:
        result = await self.db.execute(
            select(func.count(Expense.id)).where(
                Expense.user_id == user_id,
                extract("month", Expense.date) == month,
                extract("year", Expense.date) == year,
            )
        )
        return result.scalar_one()

    async def get_monthly_summary(self, user_id: int, month: int, year: int) -> dict:
        total_spent = await self._total_spent(user_id, month, year)
        total_budgeted = await self._total_budgeted(user_id, month, year)
        by_category = await self._by_category(user_id, month, year, total_spent)
        daily = await self._daily_breakdown(user_id, month, year)
        count = await self._expense_count(user_id, month, year)
        top_category = by_category[0]["category_name"] if by_category else None

        return {
            "month": month,
            "year": year,
            "total_spent": total_spent,
            "total_budgeted": total_budgeted,
            "remaining_budget": total_budgeted - total_spent,
            "expense_count": count,
            "top_category": top_category,
            "by_category": by_category,
            "daily_breakdown": daily,
        }

    async def get_trend(self, user_id: int, months: int = 6) -> list[dict]:
        result = await self.db.execute(
            select(
                extract("month", Expense.date).label("month"),
                extract("year", Expense.date).label("year"),
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("expense_count"),
            )
            .where(Expense.user_id == user_id)
            .group_by("month", "year")
            .order_by("year", "month")
            .limit(months)
        )
        return [
            {
                "month": int(row.month),
                "year": int(row.year),
                "total": Decimal(str(row.total)),
                "expense_count": row.expense_count,
            }
            for row in result.all()
        ]

    async def get_insights(self, user_id: int, month: int, year: int) -> dict:
        current = await self.get_monthly_summary(user_id, month, year)
        trend = await self.get_trend(user_id)
        return {"current_month": current, "trend": trend}