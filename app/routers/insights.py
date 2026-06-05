from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.insights import InsightsSummary, MonthlySummary
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["Insights"])

@router.get("/", response_model=InsightsSummary)
async def get_insights(
    month: int = Query(default_factory=lambda: datetime.now().month),
    year: int = Query(default_factory=lambda: datetime.now().year),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await InsightsService(db).get_insights(current_user.id, month, year)

@router.get("/monthly", response_model=MonthlySummary)
async def get_monthly(
    month: int = Query(default_factory=lambda: datetime.now().month),
    year: int = Query(default_factory=lambda: datetime.now().year),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await InsightsService(db).get_monthly_summary(current_user.id, month, year)