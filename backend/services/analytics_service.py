"""Analytics service: farm-wide KPI calculations, aggregation, and trend analysis."""

from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.models.aquaculture import Pond, FishBatch, FishHarvest, FeedLog, WaterQualityLog
from backend.models.crop import GreenhouseCrop, CropHarvest, VerticalFarmBatch, FieldCrop
from backend.models.poultry import PoultryFlock, EggCollection, DuckFlock, BeeHive
from backend.models.financial import RevenueEntry, ExpenseEntry
from backend.models.inventory import InventoryItem
from backend.models.market import CustomerOrder, Shipment
from backend.models.incident import Incident
from backend.models.production import StockLedger, ProductionBatch
from backend.models.sensor import Alert


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_kpis(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date.replace(month=1, day=1)  # YTD

        # Revenue
        revenue = self.db.query(func.coalesce(func.sum(RevenueEntry.total_amount), 0)).filter(
            RevenueEntry.entry_date.between(start_date, end_date)
        ).scalar()

        # Expenses
        expenses = self.db.query(func.coalesce(func.sum(ExpenseEntry.total_amount), 0)).filter(
            ExpenseEntry.entry_date.between(start_date, end_date)
        ).scalar()

        # Aquaculture
        total_fish_stock = self.db.query(func.coalesce(func.sum(FishBatch.current_count), 0)).filter(
            FishBatch.status == "growing"
        ).scalar()

        total_biomass = self.db.query(
            func.coalesce(func.sum(FishBatch.current_count * FishBatch.current_avg_weight_g / 1000), 0)
        ).filter(FishBatch.status == "growing").scalar()

        active_ponds = self.db.query(func.count(Pond.id)).filter(Pond.status == "active").scalar()

        # Poultry
        poultry_flock = self.db.query(PoultryFlock).filter(PoultryFlock.status == "laying").first()
        eggs_today = 0
        lay_rate = 0.0
        if poultry_flock:
            today_eggs = self.db.query(EggCollection).filter(
                and_(EggCollection.flock_id == poultry_flock.id, EggCollection.collection_date == date.today())
            ).first()
            eggs_today = today_eggs.total_eggs if today_eggs else 0
            lay_rate = poultry_flock.lay_rate_pct

        # Greenhouse crops
        active_gh_crops = self.db.query(func.count(GreenhouseCrop.id)).filter(
            GreenhouseCrop.status == "active"
        ).scalar()

        # Inventory alerts
        low_stock_items = self.db.query(func.count(InventoryItem.id)).filter(
            InventoryItem.current_stock <= InventoryItem.reorder_point,
            InventoryItem.is_active == True
        ).scalar()

        # Open incidents
        open_incidents = self.db.query(func.count(Incident.id)).filter(
            Incident.status.in_(["open", "investigating", "containment"])
        ).scalar()

        # Active alerts
        active_alerts = self.db.query(func.count(Alert.id)).filter(
            Alert.resolved == False
        ).scalar()

        # Pending orders
        pending_orders = self.db.query(func.count(CustomerOrder.id)).filter(
            CustomerOrder.order_status.in_(["confirmed", "processing", "packed"])
        ).scalar()

        return {
            "period": {"start": str(start_date), "end": str(end_date)},
            "financial": {
                "revenue": float(revenue),
                "expenses": float(expenses),
                "profit": float(revenue - expenses),
                "margin_pct": round((revenue - expenses) / revenue * 100, 1) if revenue > 0 else 0,
            },
            "aquaculture": {
                "total_stock": int(total_fish_stock),
                "biomass_tonnes": round(float(total_biomass) / 1000, 2),
                "active_ponds": int(active_ponds),
            },
            "poultry": {
                "eggs_today": eggs_today,
                "lay_rate_pct": lay_rate,
            },
            "crops": {
                "active_greenhouse_crops": int(active_gh_crops),
            },
            "operations": {
                "low_stock_items": int(low_stock_items),
                "open_incidents": int(open_incidents),
                "active_alerts": int(active_alerts),
                "pending_orders": int(pending_orders),
            },
        }

    def get_revenue_by_stream(self, start_date: date, end_date: date) -> list:
        results = self.db.query(
            RevenueEntry.stream,
            func.sum(RevenueEntry.total_amount).label("total")
        ).filter(
            RevenueEntry.entry_date.between(start_date, end_date)
        ).group_by(RevenueEntry.stream).all()

        return [{"stream": r.stream, "total": float(r.total)} for r in results]

    def get_expense_by_category(self, start_date: date, end_date: date) -> list:
        results = self.db.query(
            ExpenseEntry.category,
            func.sum(ExpenseEntry.total_amount).label("total")
        ).filter(
            ExpenseEntry.entry_date.between(start_date, end_date)
        ).group_by(ExpenseEntry.category).all()

        return [{"category": r.category, "total": float(r.total)} for r in results]

    def get_monthly_pnl(self, year: int) -> list:
        months = []
        for m in range(1, 13):
            s = date(year, m, 1)
            e = date(year, m + 1, 1) - timedelta(days=1) if m < 12 else date(year, 12, 31)

            rev = self.db.query(func.coalesce(func.sum(RevenueEntry.total_amount), 0)).filter(
                RevenueEntry.entry_date.between(s, e)
            ).scalar()

            exp = self.db.query(func.coalesce(func.sum(ExpenseEntry.total_amount), 0)).filter(
                ExpenseEntry.entry_date.between(s, e)
            ).scalar()

            months.append({
                "month": m,
                "revenue": float(rev),
                "expenses": float(exp),
                "profit": float(rev - exp),
            })
        return months
