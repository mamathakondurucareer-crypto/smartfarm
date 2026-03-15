"""Unit tests for the AnalyticsService."""

import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.services.analytics_service import AnalyticsService
from backend.models.financial import RevenueEntry, ExpenseEntry, CostCenter
from backend.models.aquaculture import Pond, FishBatch

TEST_DB = "sqlite:///./test_analytics.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)


@pytest.fixture(autouse=True, scope="module")
def analytics_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = Session()
    yield session
    session.rollback()
    session.close()


class TestAnalyticsServiceKPIs:
    def test_kpis_returns_dict(self, db):
        svc = AnalyticsService(db)
        result = svc.get_dashboard_kpis()
        assert isinstance(result, dict)

    def test_kpis_has_required_keys(self, db):
        svc = AnalyticsService(db)
        result = svc.get_dashboard_kpis()
        assert "financial" in result
        assert "aquaculture" in result
        assert "poultry" in result
        assert "crops" in result

    def test_kpis_financial_structure(self, db):
        svc = AnalyticsService(db)
        result = svc.get_dashboard_kpis()
        fin = result["financial"]
        assert "revenue" in fin
        assert "expenses" in fin
        assert "profit" in fin

    def test_kpis_empty_db_returns_zeros(self, db):
        svc = AnalyticsService(db)
        result = svc.get_dashboard_kpis()
        assert result["financial"]["revenue"] == 0
        assert result["financial"]["expenses"] == 0

    def test_kpis_with_date_range(self, db):
        svc = AnalyticsService(db)
        result = svc.get_dashboard_kpis(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        assert isinstance(result, dict)
        assert result["period"]["start"] == "2025-01-01"
        assert result["period"]["end"] == "2025-12-31"

    def test_revenue_aggregation(self, db):
        cost_center = CostCenter(code="CC-TEST", name="Test Center", department="aquaculture")
        db.add(cost_center)
        db.flush()
        db.add(RevenueEntry(
            entry_date=date(2025, 6, 1),
            stream="aquaculture",
            category="fish_sales",
            description="Rohu fish sale",
            quantity=100,
            unit_price=50.0,
            total_amount=5000.0,
            net_amount=5000.0,
        ))
        db.add(RevenueEntry(
            entry_date=date(2025, 6, 15),
            stream="poultry_eggs",
            category="egg_sales",
            description="Hen egg sale",
            quantity=200,
            unit_price=10.0,
            total_amount=2000.0,
            net_amount=2000.0,
        ))
        db.flush()
        svc = AnalyticsService(db)
        result = svc.get_dashboard_kpis(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        assert result["financial"]["revenue"] == 7000.0

    def test_profit_calculation(self, db):
        svc = AnalyticsService(db)
        result = svc.get_dashboard_kpis(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        expected_profit = result["financial"]["revenue"] - result["financial"]["expenses"]
        assert result["financial"]["profit"] == expected_profit
