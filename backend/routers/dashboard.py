"""Dashboard endpoints: aggregated KPIs and overview data."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/kpis")
def get_kpis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    svc = AnalyticsService(db)
    return svc.get_dashboard_kpis(start_date, end_date)


@router.get("/revenue-by-stream")
def revenue_by_stream(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    svc = AnalyticsService(db)
    return svc.get_revenue_by_stream(start_date, end_date)


@router.get("/expense-by-category")
def expense_by_category(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    svc = AnalyticsService(db)
    return svc.get_expense_by_category(start_date, end_date)


@router.get("/monthly-pnl")
def monthly_pnl(year: int = Query(...), db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.get_monthly_pnl(year)
